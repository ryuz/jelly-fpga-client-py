#%%
import sys
import time
from jelly_fpga_client import jelly_fpga_control

# コマンドライン引数で指定した IP アドレスに接続
target = sys.argv[1]
print("target:", target)
fpga_ctl = jelly_fpga_control.JellyFpgaControl(target)
fpga_ctl.reset()


#%%
with open("kv260_udmabuf_sample.dts", "r") as f:
    dts = f.read()
print(len(dts)) 
dtb = fpga_ctl.dts_to_dtb(dts)
print(len(dtb)) 
fpga_ctl.upload_firmware("kv260_udmabuf_sample.dtbo", dtb)


#%%
# bitstreamファイルをアップロード
fpga_ctl.upload_firmware_file("kv260_udmabuf_sample.bit", "./kv260_udmabuf_sample.bit")
# アップロードした bitstream ファイルを bin ファイルに変換
fpga_ctl.bitstream_to_bin("kv260_udmabuf_sample.bit", "kv260_udmabuf_sample.bit.bin", "zynqmp")

#%%
fpga_ctl.unload()
fpga_ctl.load_dtbo("kv260_udmabuf_sample.dtbo")

#%%
udmabuf_accessor = fpga_ctl.open_udmabuf("udmabuf-jelly-sample")
uio_accessor     = fpga_ctl.open_uio("uio_pl_peri")
dma0_accessor    = fpga_ctl.subclone(uio_accessor, 0x00000, 0x800)
dma1_accessor    = fpga_ctl.subclone(uio_accessor, 0x00800, 0x800)
led_accessor     = fpga_ctl.subclone(uio_accessor, 0x08000, 0x800)
tim_accessor     = fpga_ctl.subclone(uio_accessor, 0x10000, 0x800)

# レジスタアドレス定義
REG_DMA_STATUS  = 0
REG_DMA_WSTART  = 1
REG_DMA_RSTART  = 2
REG_DMA_ADDR    = 3
REG_DMA_WDATA0  = 4
REG_DMA_WDATA1  = 5
REG_DMA_RDATA0  = 6
REG_DMA_RDATA1  = 7
REG_DMA_CORE_ID = 8

REG_TIM_CONTROL = 0
REG_TIM_COMPARE = 1
REG_TIM_COUNTER = 3

#%%
dma0_id = fpga_ctl.read_reg_u64(dma0_accessor, REG_DMA_CORE_ID)
dma1_id = fpga_ctl.read_reg_u64(dma1_accessor, REG_DMA_CORE_ID)
print(f"DMA0 core_id: 0x{dma0_id:04x}")
print(f"DMA1 core_id: 0x{dma0_id:04x}")

# %%
# udmabuf領域アクセス
fpga_ctl.write_mem_u32(udmabuf_accessor, 0x0, 0x12345678)
fpga_ctl.write_mem_u32(udmabuf_accessor, 0x4, 0x9abcdef0)
fpga_ctl.write_mem_u32(udmabuf_accessor, 0x8, 0xdeadbeef)
fpga_ctl.write_mem_u32(udmabuf_accessor, 0xc, 0x87654321)

# udmabufの物理アドレスを取得しておく
phys_addr = fpga_ctl.get_phys_addr(udmabuf_accessor)

#%%
# DMA0でread

fpga_ctl.write_reg_u64(dma0_accessor, REG_DMA_ADDR,   phys_addr)
fpga_ctl.write_reg_u64(dma0_accessor, REG_DMA_RSTART, 1)
time.sleep(0.1)
dma0_rdata0 = fpga_ctl.read_reg_u64(dma0_accessor, REG_DMA_RDATA0)
dma0_rdata1 = fpga_ctl.read_reg_u64(dma0_accessor, REG_DMA_RDATA1)

print(f"DMA0 RDATA0: 0x{dma0_rdata0:016x}")
print(f"DMA0 RDATA1: 0x{dma0_rdata1:016x}")

#%%
# DMA1でwrite
fpga_ctl.write_reg_u64(dma1_accessor, REG_DMA_ADDR,   phys_addr)
fpga_ctl.write_reg_u64(dma1_accessor, REG_DMA_WDATA0, 0xfedcba9876543210)
fpga_ctl.write_reg_u64(dma1_accessor, REG_DMA_WDATA1, 0x0123456789abcdef)
fpga_ctl.write_reg_u64(dma1_accessor, REG_DMA_WSTART, 1)
time.sleep(0.1)
udmabuf_rdata0 = fpga_ctl.read_mem_u32(udmabuf_accessor, 0x0)
udmabuf_rdata1 = fpga_ctl.read_mem_u32(udmabuf_accessor, 0x4)
udmabuf_rdata2 = fpga_ctl.read_mem_u32(udmabuf_accessor, 0x8)
udmabuf_rdata3 = fpga_ctl.read_mem_u32(udmabuf_accessor, 0xc)
print(f"udmabuf_rdata0: 0x{udmabuf_rdata0:08x}")
print(f"udmabuf_rdata1: 0x{udmabuf_rdata1:08x}")
print(f"udmabuf_rdata2: 0x{udmabuf_rdata2:08x}")
print(f"udmabuf_rdata3: 0x{udmabuf_rdata3:08x}")

# %%
# LEDを点滅させる
for _ in range(3):
    print("LED ON")
    fpga_ctl.write_reg_u(led_accessor, 0, 1)
    time.sleep(0.5)
    print("LED OFF")
    fpga_ctl.write_reg_u(led_accessor, 0, 0)
    time.sleep(0.5)


#%%
# close
fpga_ctl.close(tim_accessor)
fpga_ctl.close(led_accessor)
fpga_ctl.close(dma1_accessor)
fpga_ctl.close(dma0_accessor)
fpga_ctl.close(uio_accessor)
fpga_ctl.close(udmabuf_accessor)

# 後始末
fpga_ctl.remove_firmware("kv260_udmabuf_sample.dtbo")
fpga_ctl.remove_firmware("kv260_udmabuf_sample.bit")
fpga_ctl.remove_firmware("kv260_udmabuf_sample.bit.bin")

fpga_ctl.unload()
fpga_ctl.load("k26-starter-kits")

# %%
