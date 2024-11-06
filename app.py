# Certifique-se de que o ffmpeg está instalado no Colab
import os
import re
from pytubefix import YouTube
from urllib.parse import urlparse, parse_qs
from moviepy.editor import VideoFileClip, AudioFileClip
# from google.colab import files  # Para fazer o download do arquivo para o computador

def limpar_url(url):
    parsed_url = urlparse(url)
    video_id = parse_qs(parsed_url.query).get('v')
    if video_id:
        return f"https://youtube.com/watch?v={video_id[0]}"
    else:
        return url.split('?')[0]

def limpar_nome(nome):
   
    return re.sub(r'[<>:"/\\|?*]', "", nome)

def baixar_video():
    try:
        url = input("Insira a url do vídeo:\n")
        url = limpar_url(url)
        yt = YouTube(url)

        titulo_video = limpar_nome(yt.title) 
        print("Baixando:", titulo_video)

        video_streams = yt.streams.filter(type="video", file_extension="mp4").order_by("resolution").desc()
        audio_streams = yt.streams.filter(type="audio", file_extension="mp4").order_by("abr").desc()

        if not video_streams or not audio_streams:
            print("Nenhuma qualidade disponível para este vídeo.")
            return

        melhores_streams = {}
        for stream in video_streams:
            if stream.resolution not in melhores_streams:
                melhores_streams[stream.resolution] = stream
            else:
                atual = melhores_streams[stream.resolution]
                if (stream.bitrate > atual.bitrate) or (stream.fps > atual.fps):
                    melhores_streams[stream.resolution] = stream

        opcoes_video = {i + 1: stream for i, stream in enumerate(melhores_streams.values())}
        print("Qualidades de vídeo disponíveis:")
        for i, stream in opcoes_video.items():
            print(f"{i}: {stream.resolution} - {stream.bitrate}bps, {stream.fps}fps")

        escolha = input(f"Escolha a qualidade (1 a {len(opcoes_video)}) ou pressione Enter para a melhor disponível:\n")
        video_stream_desejado = opcoes_video.get(int(escolha), next(iter(melhores_streams.values())))
        audio_stream_desejado = audio_streams.first()

        formato_download = input("Escolha a opção de download:\n1: Apenas vídeo com áudio integrado\n2: Vídeo e áudio separados, juntamente com o vídeo final\n")

        if formato_download == '1':
            print(f"Baixando vídeo em {video_stream_desejado.resolution} com áudio integrado...")
            video_com_audio = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
            if video_com_audio:
                video_com_audio.download(filename='video_final.mp4')
              #  files.download('video_final.mp4')  # Baixa o arquivo para o seu computador
                print("Vídeo com áudio integrado baixado com sucesso :)")
            else:
                print("Não foi possível encontrar um stream de vídeo com áudio integrado.")

        elif formato_download == '2':
            if video_stream_desejado and audio_stream_desejado:
                print(f"Baixando vídeo em {video_stream_desejado.resolution}...")
                video_stream_desejado.download(filename='video.mp4')
                print(f"Baixando áudio em {audio_stream_desejado.abr}...")
                audio_stream_desejado.download(filename='audio.mp4')

                print("Combinando vídeo e áudio...")
                video_clip = VideoFileClip('video.mp4')
                audio_clip = AudioFileClip('audio.mp4')
                video_com_audio = video_clip.set_audio(audio_clip)  # Integrando o áudio no vídeo

                video_com_audio.write_videofile('video_final.mp4', codec='libx264', audio_codec='aac')

                video_clip.close()
                audio_clip.close()
                print("Vídeo e áudio baixados, combinados e baixados com sucesso :)")

                # Renomeia o arquivo final com o nome original do vídeo, após a combinação
                os.rename('video_final.mp4', f"{titulo_video}.mp4")
                # files.download(f"{titulo_video}.mp4")  # Baixa o arquivo final para o seu computador
                print("Arquivo renomeado e pronto para download.")

        else:
            print("Opção inválida. Nenhum download realizado.")

    except Exception as e:
        print("Ocorreu um erro:", e)



baixar_video()
