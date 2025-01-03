import sys
import time
from jelly_fpga_client import jelly_fpga_control

#%%
# コマンドライン引数で指定した IP アドレスに接続
target = sys.argv[1]
print("target:", target)
fpga_ctl = jelly_fpga_control.JellyFpgaControl(target)
fpga_ctl.reset()

dts = """\
/dts-v1/; /plugin/;

/ {
    fragment@0 {
        target = <&fpga_full>;
        overlay0: __overlay__ {
            #address-cells = <2>;
            #size-cells = <2>;
            firmware-name = "kv260_blinking_led_ps.bit.bin";
        };
    };

    fragment@1 {
        target = <&amba>;
        overlay1: __overlay__ {
            clocking0: clocking0 {
                #clock-cells = <0>;
                assigned-clock-rates = <100000000>;
                assigned-clocks = <&zynqmp_clk 71>;
                clock-output-names = "fabric_clk";
                clocks = <&zynqmp_clk 71>;
                compatible = "xlnx,fclk";
            };
        };
    };
};
"""

# DTBに変換して firmware としてアップロード
dtb = fpga_ctl.dts_to_dtb(dts)
fpga_ctl.upload_firmware("kv260_blinking_led_ps.dtbo", dtb)

#%%
# bitstreamファイルをアップロード
fpga_ctl.upload_firmware_file("kv260_blinking_led_ps.bit", "./kv260_blinking_led_ps.bit")
# アップロードした bitstream ファイルを bin ファイルに変換
fpga_ctl.bitstream_to_bin("kv260_blinking_led_ps.bit", "kv260_blinking_led_ps.bit.bin", "zynqmp")

#%%
fpga_ctl.unload()
fpga_ctl.load_dtbo("kv260_blinking_led_ps.dtbo")

#%%
# /dev/mem を mmap して LED0 を点滅させる
accessor = fpga_ctl.open_mmap("/dev/mem", 0xa0000000, 0x1000)
for _ in range(3):
    fpga_ctl.write_mem_u64(accessor, 0, 1) # LED0 ON
    time.sleep(0.5)
    fpga_ctl.write_mem_u64(accessor, 0, 0) # LED0 OFF
    time.sleep(0.5)

#%%
# close
fpga_ctl.close(accessor)

# 後始末
fpga_ctl.remove_firmware("kv260_blinking_led_ps.dtbo")
fpga_ctl.remove_firmware("kv260_blinking_led_ps.bit")
fpga_ctl.remove_firmware("kv260_blinking_led_ps.bit.bin")


fpga_ctl.unload()
fpga_ctl.load("k26-starter-kits")
