
#%%
import sys
print("Python version:", sys.version)
print("sys.prefix:", sys.prefix)
print("sys.base_prefix:", sys.base_prefix)
#sys.exit(0)

#%%
from jelly_fpga_client import jelly_fpga_control

ftga_ctl = jelly_fpga_control.JellyFpgaControl("10.72.141.82:50051")
ftga_ctl.reset()


#%%
with open("kv260_udmabuf_sample.dts", "r") as f:
    dts = f.read()
print(len(dts)) 
dtb = ftga_ctl.dts_to_dtb(dts)
print(len(dtb)) 
ftga_ctl.upload_firmware("kv260_udmabuf_sample.dtbo", dtb)


#%%
# bitstreamファイルをアップロード
ftga_ctl.upload_firmware_file("kv260_udmabuf_sample.bit", "./kv260_udmabuf_sample.bit")
# アップロードした bitstream ファイルを bin ファイルに変換
ftga_ctl.bitstream_to_bin("kv260_udmabuf_sample.bit", "kv260_udmabuf_sample.bit.bin", "zynqmp")

#%%
ftga_ctl.unload()
ftga_ctl.load_dtbo("kv260_udmabuf_sample.dtbo")

#%%
udmabuf_accessor = ftga_ctl.open_udmabuf("udmabuf-jelly-sample")
uio_accessor     = ftga_ctl.open_uio("uio_pl_peri")
dma0_accessor    = ftga_ctl.subclone(uio_accessor, 0x00000, 0x800)
dma1_accessor    = ftga_ctl.subclone(uio_accessor, 0x00800, 0x800)
led_accessor     = ftga_ctl.subclone(uio_accessor, 0x08000, 0x800)
tim_accessor     = ftga_ctl.subclone(uio_accessor, 0x10000, 0x800)

# %%
udmabuf_accessor
# %%
