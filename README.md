# jelly-fpga-client-python

Pythonクライアントライブラリfor Jelly FPGAサーバー。gRPCを使用してFPGAビットストリームの管理やメモリマップドアクセスを行います。

## 概要

このライブラリは以下の機能を提供します：

- FPGAビットストリームのロード/アンロード
- ファームウェアのアップロード
- Device Tree Overlayの管理
- メモリマップドアクセス（UIO、UDMABUFなど）
- gRPCを使ったリモートFPGA制御

## 必要な環境

- Python 3.7 以上
- jelly-fpga-server（Rustで実装されたサーバー）

## インストール方法

### 1. 仮想環境の作成（推奨）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# または
venv\Scripts\activate     # Windows
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. パッケージのインストール

#### 開発用インストール（推奨）
ソースコードを変更しながら開発する場合：

```bash
pip install -e .
```

#### 通常のインストール
```bash
pip install .
```

## 使用方法

### 基本的な使い方

```python
from jelly_fpga_client import jelly_fpga_control

# サーバーに接続（デフォルトはlocalhost:8051）
fpga_ctl = jelly_fpga_control.JellyFpgaControl("10.72.141.82:8051")

# FPGAをリセット
fpga_ctl.reset()

# ビットストリームファイルをアップロード
with open("bitstream.bit", "rb") as f:
    data = f.read()
fpga_ctl.upload_firmware("bitstream.bit", data)

# ビットストリームをロード
fpga_ctl.load_bitstream("bitstream.bit")

# Device Tree Source文字列からDTBを生成
dts_content = """
/dts-v1/; /plugin/;
/ {
    fragment@0 {
        target = <&fpga_full>;
        __overlay__ {
            firmware-name = "bitstream.bit.bin";
        };
    };
};
"""
dtb_data = fpga_ctl.dts_to_dtb(dts_content)

# メモリマップドアクセス
mmap_id = fpga_ctl.open_mmap(0x80000000, 0x1000)  # アドレス、サイズ
fpga_ctl.write_mem32(mmap_id, 0x0, 0x12345678)    # オフセット、値
value = fpga_ctl.read_mem32(mmap_id, 0x0)         # オフセット
fpga_ctl.close_mmap(mmap_id)
```

### サンプルコード

#### LEDブリンキングの例

```python
import sys
import time
from jelly_fpga_client import jelly_fpga_control

# サーバーに接続
target = "10.72.141.82:8051"  # または sys.argv[1]
fpga_ctl = jelly_fpga_control.JellyFpgaControl(target)
fpga_ctl.reset()

# ビットストリームファイルをアップロード
with open("kv260_blinking_led_ps.bit", "rb") as f:
    data = f.read()
fpga_ctl.upload_firmware("kv260_blinking_led_ps.bit", data)

# Device Tree Overlayを設定
dts = '''
/dts-v1/; /plugin/;
/ {
    fragment@0 {
        target = <&fpga_full>;
        __overlay__ {
            firmware-name = "kv260_blinking_led_ps.bit.bin";
        };
    };
    fragment@1 {
        target = <&amba>;
        __overlay__ {
            led_controller: led_controller@80000000 {
                compatible = "generic-uio";
                reg = <0x0 0x80000000 0x0 0x1000>;
            };
        };
    };
};
'''

# DTBを生成してロード
dtb_data = fpga_ctl.dts_to_dtb(dts)
fpga_ctl.upload_firmware("overlay.dtb", dtb_data)
fpga_ctl.load_dtbo("overlay.dtb")

# メモリマップドアクセスでLEDを制御
mmap_id = fpga_ctl.open_mmap(0x80000000, 0x1000)

# LEDを点滅
for i in range(10):
    fpga_ctl.write_mem32(mmap_id, 0x0, 1)  # LED ON
    time.sleep(0.5)
    fpga_ctl.write_mem32(mmap_id, 0x0, 0)  # LED OFF
    time.sleep(0.5)

fpga_ctl.close_mmap(mmap_id)
```

## API リファレンス

### JellyFpgaControl クラス

#### コンストラクタ
- `JellyFpgaControl(target="localhost:8051")`: サーバーに接続

#### FPGA制御メソッド
- `reset()`: FPGAをリセット
- `load(name)`: 指定されたファームウェアをロード
- `unload(slot=0)`: 指定されたスロットをアンロード

#### ファームウェア管理
- `upload_firmware(name, data, chunk_size=2MB)`: ファームウェアをアップロード
- `remove_firmware(name)`: ファームウェアを削除
- `load_bitstream(name)`: ビットストリームをロード
- `load_dtbo(name)`: Device Tree Overlayをロード

#### 変換ユーティリティ
- `dts_to_dtb(dts)`: Device Tree SourceをBinaryに変換
- `bitstream_to_bin(bitstream_name, bin_name, arch="zynqmp")`: ビットストリームをバイナリに変換

#### メモリアクセス
- `open_mmap(address, size)`: メモリマップドアクセスを開く
- `close_mmap(mmap_id)`: メモリマップドアクセスを閉じる
- `read_mem32(mmap_id, offset)`: 32ビット読み取り
- `write_mem32(mmap_id, offset, value)`: 32ビット書き込み
- `read_mem64(mmap_id, offset)`: 64ビット読み取り
- `write_mem64(mmap_id, offset, value)`: 64ビット書き込み

#### UIO/UDMABUF サポート
- `open_uio(name)`: UIOデバイスを開く
- `open_udmabuf(name)`: UDMABUFデバイスを開く

## テスト

テストスクリプトを実行：

```bash
cd tests
python test_blinking_led.py <server_address:port>
python test_udmabuf.py <server_address:port>
```

例：
```bash
python test_blinking_led.py 10.72.141.82:8051
```

## 開発

### 依存関係

主な依存関係（requirements.txtを参照）：
- grpcio: gRPC通信
- grpcio-tools: protobufコンパイル
- protobuf: プロトコルバッファ

### プロトコルバッファの再生成

```bash
python gen_.py
```

## ライセンス

MIT License

## 著者

Ryuji Fuchikami (ryuji.fuchikami@nifty.com)

## 関連プロジェクト

- [jelly-fpga-server](https://github.com/ryuz/jelly-fpgautil-rs) - Rustで実装されたFPGAサーバー
- [jelly-fpgautil-rs](https://github.com/ryuz/jelly-fpgautil-rs) - FPGAユーティリティライブラリ
