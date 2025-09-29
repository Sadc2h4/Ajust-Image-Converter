import os
import sys
from sys import argv
import io

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QLineEdit, 
                            QVBoxLayout, QWidget, QMessageBox, QCheckBox, QProgressBar, QHBoxLayout)
from PyQt5.QtGui import QIcon

from PIL import Image
from datetime import datetime  # 日付取得用

# exe/onefile/onedir を問わず“実行時のリソース配置場所”を返す
def _base_dir():
    # onefile 実行時は PyInstaller が展開する一時フォルダ
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    # onedir 実行時は exe のあるフォルダ
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # 開発時（素の python 実行）
    return os.path.dirname(os.path.abspath(__file__))

# アプリの土台パス（リソースのルート）
BASE_DIR = _base_dir()

# 既存コードに合わせた従来変数
dir_name = os.path.dirname(os.path.abspath(argv[0]))  # exe のあるフォルダ
cwd = os.path.dirname(__file__)                       # スクリプト参照用（開発時に使用）
#===========================================================================================
class ImageConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # ウィンドウのアイコンを設定
        exe_icon_path = os.path.join(cwd, "exe_logo.png")
        self.setWindowIcon(QIcon(exe_icon_path))

    def init_ui(self):
        self.setWindowTitle("Ajust Image Converter")
        self.setGeometry(100, 100, 600, 300)

        # メインウィジェットとレイアウト
        Base_Widget = QWidget(self)
        self.setCentralWidget(Base_Widget)
        mainLayout = QVBoxLayout(Base_Widget)

        # ラベルとテキストボックス
        Discription_text =("\nThis application is an image conversion tool that \n"
                            "converts all images in a specified folder to png images\n"
                            "and saves them in a “convert” folder for output.\n")
        self.label = QLabel(Discription_text)
        mainLayout.addWidget(self.label)

        self.file_name_label = QLabel("Set the file name to be used for numbering.↓")
        mainLayout.addWidget(self.file_name_label)

        self.file_name_input = QLineEdit(self)
        self.file_name_input.setPlaceholderText("Specify the file name (if not specified, “Convert” will be used).")
        mainLayout.addWidget(self.file_name_input)

        # ---------------------------------------------------------
        checkbox_Layout1 = QHBoxLayout()
        # 左右反転機能のチェックボックス
        self.mirror_checkbox = QCheckBox("Create left-to-right flipped image")
        checkbox_Layout1.addWidget(self.mirror_checkbox)

        # 画像サイズ自動変換のチェックボックス
        self.resize_checkbox = QCheckBox("Automatic image size conversion")
        checkbox_Layout1.addWidget(self.resize_checkbox)

        checkbox_Layout2 = QHBoxLayout()
        # 画像鮮明化のチェックボックス
        self.pixelart_checkbox = QCheckBox("Sharpen enlarged images")
        checkbox_Layout2.addWidget(self.pixelart_checkbox)

        # 背景透過のチェックボックス
        self.removeBG_checkbox = QCheckBox("background removed")
        checkbox_Layout2.addWidget(self.removeBG_checkbox)

        mainLayout.addLayout(checkbox_Layout1)
        mainLayout.addLayout(checkbox_Layout2)
        # ---------------------------------------------------------
        # ボタン
        self.button = QPushButton("Select the folder to be converted")
        self.button.clicked.connect(self.select_folder)
        mainLayout.addWidget(self.button)

        self.convert_button = QPushButton("Start Conversion")
        self.convert_button.setEnabled(False)  # 初期状態で無効化
        self.convert_button.setStyleSheet("color: gray; height: 70px;")
        self.convert_button.clicked.connect(self.convert_images)
        mainLayout.addWidget(self.convert_button)

        # ---------------------------------------------------------
        # 進捗バー
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        mainLayout.addWidget(self.progress_bar)

        Base_Widget .setLayout(mainLayout)
        self.setCentralWidget(Base_Widget )
        
        # ステータスバーの作成
        self.statusBar().showMessage("Folder currently selected : not selected")

        self.source_folder = None
        self.destination_folder = None

        # ---------------------------------------------------------

    def remove_background(self, image):
        # --------------------------------------------------------------------
        # 画像背景を消去する処理
        # --------------------------------------------------------------------
        try:
            # 画像をバイトストリームに変換
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="PNG")  # PIL 画像を PNG 形式で保存
            img_byte_arr.seek(0)  # ストリームの先頭にポインタを戻す

            # 背景を除去
            from rembg import remove # 重い処理の為,背景消去の処理の時のみ呼ぶ
            result = remove(img_byte_arr.getvalue())  # バイトストリームを渡す
            result_image = Image.open(io.BytesIO(result))  # 背景除去後の画像を読み込む

            if result_image.mode in ("P", "RGBA"):
                result_image = result_image.convert("RGBA")
                background = Image.new("RGBA", result_image.size, (255, 255, 255, 255))
                result_image = Image.alpha_composite(background, result_image).convert("RGB")

            return result_image

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during the background removal process : {str(e)}")
            return None


    def resize_with_aspect_ratio(self, image):
        # --------------------------------------------------------------------
        # 縦横比を維持しながら、指定されたサイズに画像をリサイズし、余白を埋める
        # --------------------------------------------------------------------
        # 元の画像を縦横比を維持したままリサイズ
        # 透過画像の場合は RGBA モードに変換

        if image.mode in ("P", "RGBA"):
            image = image.convert("RGBA")
            background = Image.new("RGBA", image.size, (255, 255, 255, 255))
            image = Image.alpha_composite(background, image).convert("RGB")

        # 元画像のサイズ取得
        original_width, original_height = image.size

        # ターゲットサイズの決定
        if original_height > original_width + 200:
            target_width, target_height = 832, 1216
        elif original_width > original_height + 200:
            target_width, target_height = 1216, 832
        else:
            target_width, target_height = 1024, 1024

        # 比率を計算してリサイズする
        scale = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)

        # リサイズ処理
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 背景を白で塗りつぶしたターゲットサイズの画像を作成
        new_image = Image.new("RGB", (target_width, target_height), (255, 255, 255))

        # 画像を中央に貼り付け
        offset_x = (target_width - new_width) // 2
        offset_y = (target_height - new_height) // 2
        new_image.paste(resized_image, (offset_x, offset_y))

        return new_image

    def resize_pixel_image(self, image_path, scale_factor=4):
        # --------------------------------------------------------------------
        # Pixelアートをシャギーなしで拡大する
        # --------------------------------------------------------------------
        # 画像を開く
        with Image.open(image_path) as img:
            # 画像がRGBAまたはRGB以外のモードなら変換する
            if img.mode == 'P':  # パレットモードの場合はRGBに変換
                img = img.convert('RGB')
            elif img.mode == 'LA':  # グレースケール+アルファの場合も適切に変換
                img = img.convert('RGBA')

            # 画像にアルファチャンネルがある場合は分離して拡大後に再結合
            if img.mode == 'RGBA':
                r, g, b, a = img.split()  # RGBAから各チャンネルを分離
                # 各チャンネルをNEAREST補間で拡大
                new_size = (img.width * scale_factor, img.height * scale_factor)
                r = r.resize(new_size, Image.NEAREST)
                g = g.resize(new_size, Image.NEAREST)
                b = b.resize(new_size, Image.NEAREST)
                a = a.resize(new_size, Image.NEAREST)
                # チャンネルを再結合
                new_image = Image.merge('RGBA', (r, g, b, a))
            else:
                # アルファチャンネルがない場合はそのまま拡大
                new_size = (img.width * scale_factor, img.height * scale_factor)
                new_image = img.resize(new_size, Image.NEAREST)  # ピクセル補間法

            return new_image

    def select_folder(self):
        # --------------------------------------------------------------------
        # ダイアログからフォルダを指定する処理
        # --------------------------------------------------------------------
        folder = QFileDialog.getExistingDirectory(self, "Select target folder", dir_name)
        if folder:
            self.source_folder = folder
            self.statusBar().showMessage(f"Folder currently selected : {folder}")
            self.convert_button.setEnabled(True)  # フォルダ選択後に有効化
            self.convert_button.setStyleSheet("color: red; height: 70px;")

    def convert_images(self):
        # --------------------------------------------------------------------
        # 変換ボタンを押した際の処理
        # --------------------------------------------------------------------
        if not self.source_folder:
            return

        file_name = self.file_name_input.text().strip()
        if not file_name:
            file_name = "convert_"
        

        # 現在の日付を取得してフォルダ名に組み込む
        today = datetime.now().strftime("%Y.%m.%d.%H%M%S")
        self.destination_folder = os.path.join(dir_name, f"{today}_convert")
        os.makedirs(self.destination_folder, exist_ok=True)

        if self.removeBG_checkbox.isChecked():
            try:
                from rembg import remove  # ここで遅延 import
                # 1x1 の白画像で初回モデル/プロバイダを起動しておく
                dummy = Image.new("RGB", (1, 1), (255, 255, 255))
                buf = io.BytesIO()
                dummy.save(buf, format="PNG")
                buf.seek(0)
                _ = remove(buf.getvalue())
                os.makedirs(os.path.join(self.destination_folder, "removeBG"), exist_ok=True)
            except Exception as e:
                # 失敗しても致命傷ではないのでログだけ
                print("warm-up failed:", e)

        # 画像変換処理
        self.convert_and_rename_images(self.source_folder, self.destination_folder, file_name)
        QMessageBox.information(self, "Processing Completion", "Conversion is complete!")

    def convert_and_rename_images(self, source_folder, destination_folder, file_name):
        # --------------------------------------------------------------------
        # フォルダ内の画像カウント・メイン変換処理
        # --------------------------------------------------------------------
        image_files = [f for f in os.listdir(source_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif','.PNG','.JPEG','.bmp'))]
        total_files = len(image_files)

        if total_files == 0:
            QMessageBox.warning(self, "Error", "Image to be converted not found!")
            return
        
        self.progress_bar.setMaximum(total_files)  # 進捗バーの最大値を設定
        
        count = 1
        for filename in image_files:
            image_path = os.path.join(source_folder, filename)
            new_filename = f"{count:02d}_{file_name}.png"
            new_path = os.path.join(destination_folder, new_filename)
            image = Image.open(image_path)

            # 画像の変換
            try:
                # 画像鮮明化が選択されている場合
                if self.pixelart_checkbox.isChecked():
                    image =self.resize_pixel_image(image_path)
                
                # リサイズチェックボックスが選択されている場合
                if self.resize_checkbox.isChecked():
                    image = self.resize_with_aspect_ratio(image)

                image.save(new_path, format="PNG")
                
                # 背景透過が選択されている場合
                if self.removeBG_checkbox.isChecked():
                    removeBG_image = self.remove_background(image)
                    removeBG_filename = f"{count:02d}_{file_name}_removeBG.png"
                    removeBG_path = os.path.join(destination_folder, "removeBG", removeBG_filename)
                    removeBG_image.save(removeBG_path, format="PNG")

                # 左右反転画像を作成する場合
                if self.mirror_checkbox.isChecked():
                    mirrored_image = image.transpose(Image.FLIP_LEFT_RIGHT)
                    mirrored_filename = f"{count:02d}_{file_name}_mirrored.png"
                    mirrored_path = os.path.join(destination_folder, mirrored_filename)
                    mirrored_image.save(mirrored_path, format="PNG")

                    if self.removeBG_checkbox.isChecked():
                        removeBG_image = self.remove_background(mirrored_image)
                        removeBG_filename = f"{count:02d}_{file_name}_removeBG_mirrored.png"
                        removeBG_path = os.path.join(destination_folder, "removeBG", removeBG_filename)
                        removeBG_image.save(removeBG_path, format="PNG")
                
                self.progress_bar.setValue(count - 1)  # 進捗バーを更新
                count += 1
            except Exception as e:
                print(f"Error : Could not convert {filename} - {e}")

        self.progress_bar.setValue(total_files)  # 処理完了時に進捗バーを100%に設定

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = ImageConverterApp()
    main_window.show()
    sys.exit(app.exec_())
