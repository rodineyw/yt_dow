import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QComboBox,
    QFileDialog,
    QProgressBar,
)
from pytube import YouTube
import subprocess


class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("YouTube Download")
        self.setGeometry(100, 100, 400, 200)
        layout = QVBoxLayout()

        # Entrada de URL
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Insira a URL do vídeo do YouTube aqui")
        layout.addWidget(self.url_input)

        # ComboBox de Resolução
        self.resolution_combo = QComboBox(self)
        layout.addWidget(self.resolution_combo)

        # Botão para Carregar Informações do Vídeo
        self.load_button = QPushButton("Carregar", self)
        self.load_button.clicked.connect(self.load_video_info)
        layout.addWidget(self.load_button)

        # Botão para Baixar
        self.download_button = QPushButton("Baixar", self)
        self.download_button.clicked.connect(self.download)
        layout.addWidget(self.download_button)

        # Barra de Progresso
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Label de Status
        self.status_label = QLabel("Status: Pronto", self)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def load_video_info(self):
        url = self.url_input.text()
        self.yt = YouTube(url, on_progress_callback=self.progress_function)
        self.resolution_combo.clear()
        video_streams = (
            self.yt.streams.filter(only_video=True).order_by("resolution").desc()
        )
        for stream in video_streams:
            self.resolution_combo.addItem(
                f"{stream.resolution} - {stream.mime_type}", stream
            )

    def sanitize_filename(self, title):
        invalid_chars = r'/\\?%*:|"<>.'
        for char in invalid_chars:
            title = title.replace(char, "-")
        return title

    def download(self):
        video_stream = self.resolution_combo.currentData()
        audio_stream = self.yt.streams.get_audio_only()
        suggested_title = self.sanitize_filename(self.yt.title) + ".mp4"
        file_info = QFileDialog.getSaveFileName(
            self, "Salvar Vídeo", suggested_title, "MP4 Files (*.mp4)"
        )

        if file_info[0]:
            video_path = file_info[0]
            audio_path = video_path.rsplit(".", 1)[0] + "_audio.mp4"
            output_path = video_path.rsplit(".", 1)[0] + "_final.mp4"

            try:
                self.status_label.setText("Baixando vídeo...")
                video_stream.download(filename=video_path)
                self.status_label.setText("Baixando áudio...")
                audio_stream.download(filename=audio_path)

                self.status_label.setText("Combinando vídeo e áudio...")
                self.combine_audio_video(video_path, audio_path, output_path)
                self.status_label.setText(
                    "Download e combinação concluídos com sucesso!"
                )
            except ImportError as e:
                self.status_label.setText(
                    "Falha durante o download/combinacao: " + str(e)
                )
        else:
            self.status_label.setText("Download cancelado.")

    def combine_audio_video(self, video_path, audio_path, output_path):
        command = [
            "ffmpeg",
            "-i",
            video_path,
            "-i",
            audio_path,
            "-c:v",
            "copy",
            "-c:a",
            "aac," "-strict",
            "experimental",
            output_path,
        ]
        subprocess.run(command, check=True, shell=True)
        self.progress_bar.setValue(100)

    def progress_function(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = int(bytes_downloaded / total_size * 100)
        self.progress_bar.setValue(percentage_of_completion)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = YouTubeDownloader()
    ex.show()
    sys.exit(app.exec())
