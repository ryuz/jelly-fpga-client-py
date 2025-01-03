from jelly_fpga_client import jelly_fpga_control

ftga_ctl = jelly_fpga_control.JellyFpgaControl("10.72.141.82:50051")
ftga_ctl.reset()

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
dtb = ftga_ctl.dts_to_dtb(dts)
ftga_ctl.upload_firmware("kv260_blinking_led_ps.dtbo", dtb)

#%%
# bitstreamファイルをアップロード
ftga_ctl.upload_firmware_file("kv260_blinking_led_ps.bit", "./kv260_blinking_led_ps.bit")
# アップロードした bitstream ファイルを bin ファイルに変換
ftga_ctl.bitstream_to_bin("kv260_blinking_led_ps.bit", "kv260_blinking_led_ps.bit.bin", "zynqmp")

#%%
ftga_ctl.unload()
ftga_ctl.load_dtbo("kv260_blinking_led_ps.dtbo")

#%%
# /dev/mem を mmap して LED0 を点滅させる
import time
accessor = ftga_ctl.open_mmap("/dev/mem", 0xa0000000, 0x1000)
for _ in range(3):
    ftga_ctl.write_mem_u64(accessor, 0, 1) # LED0 ON
    time.sleep(0.5)
    ftga_ctl.write_mem_u64(accessor, 0, 0) # LED0 OFF
    time.sleep(0.5)

# close
ftga_ctl.close(accessor)


#ftga_ctl.load_dtbo("kv260_sample_led0.dtbo")
#ftga_ctl.load("kv260_sample_led0")

ftga_ctl.remove_firmware("kv260_blinking_led_ps.dtbo")
ftga_ctl.remove_firmware("kv260_blinking_led_ps.bit")
ftga_ctl.remove_firmware("kv260_blinking_led_ps.bit.bin")


ftga_ctl.unload()
#ftga_ctl.load_bin("kv260_sample_led1.bit.bin")
ftga_ctl.load("kv260_sample_led1")
