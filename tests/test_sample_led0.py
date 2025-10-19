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
            firmware-name = "kv260_sample_led0.bit.bin";
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
fpga_ctl.upload_firmware("kv260_sample_led0.dtbo", dtb)

#%%
# bitstreamファイルをアップロード
fpga_ctl.upload_firmware_file("kv260_sample_led0.bit", "./kv260_sample_led0.bit")
# アップロードした bitstream ファイルを bin ファイルに変換
fpga_ctl.bitstream_to_bin("kv260_sample_led0.bit", "kv260_sample_led0.bit.bin", "zynqmp")

#%%
fpga_ctl.unload()
fpga_ctl.load_dtbo("kv260_sample_led0.dtbo")

# 3秒間待つ
time.sleep(3)


# 後始末
fpga_ctl.remove_firmware("kv260_sample_led0.dtbo")
fpga_ctl.remove_firmware("kv260_sample_led0.bit")
fpga_ctl.remove_firmware("kv260_sample_led0.bit.bin")

fpga_ctl.unload()
fpga_ctl.load("k26-starter-kits")
