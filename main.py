import subprocess
import json
import sys
import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--input', required=True, help='Ruta del archivo o carpeta a analizar')
parser.add_argument('-o', '--output', required=False, help='Ruta del archivo o carpeta de salida')
parser.add_argument('--delete-after', action='store_true', help='Borrar los archivos de origen después de procesarlos')

args = parser.parse_args()

def get_mkv_metadata(input_file):
    command = [
        'mkvmerge',
        '--identify', input_file,
        '--identification-format', 'json'
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error al ejecutar mkvmerge: {result.stderr}")
        sys.exit(1)
    metadata = json.loads(result.stdout)
    return metadata

def process_tracks(metadata):
    video_tracks = []
    audio_tracks = []
    subtitle_tracks = []

    for track in metadata['tracks']:
        if track['type'] == 'video':
            video_tracks.append(track)
        elif track['type'] == 'audio':
            audio_tracks.append(track)
        elif track['type'] == 'subtitles':
            subtitle_tracks.append(track)

    processed_audio_tracks = []
    default_spa_audio_set = False
    default_audio_set = False

    for track in audio_tracks:
        lang = track['properties'].get('language_ietf', track['properties'].get('language'))
        title = track['properties'].get('track_name', '').lower()
        if lang == 'es-419' or 'lat' in title:
            track['properties']['track_name'] = 'Spanish (Latin America)'
            track['properties']['language_ietf'] = 'es-419'
            track['properties']['default_track'] = True
            processed_audio_tracks.append(track)
            default_spa_audio_set = True
            break

    if not default_spa_audio_set:
        for track in audio_tracks:
            lang = track['properties'].get('language')
            title = track['properties'].get('track_name', '').lower()
            lang_code = track['properties'].get('language_ietf', track['properties'].get('language'))
            if lang == 'spa':
                if 'lat' in title or lang_code == 'es-419':
                    track['properties']['track_name'] = 'Spanish (Latin America)'
                    track['properties']['language_ietf'] = 'es-419'
                else:
                    # Si tiene "European" en el nombre o el codigo es es-ES, se cambia a "Spanish (Spain)" y el idioma a es-724
                    if (lang_code == 'es-ES' or lang_code == 'es-724') or 'europ' in title:
                        track['properties']['track_name'] = 'Spanish (Spain)'
                        track['properties']['language_ietf'] = 'es-ES'
                    else:
                        track['properties']['track_name'] = 'Spanish'
                track['properties']['default_track'] = True
                processed_audio_tracks.append(track)
                default_spa_audio_set = True
                break

    for track in audio_tracks:
        lang = track['properties'].get('language')
        if lang == 'jpn':
            track['properties']['track_name'] = 'Japanese'
            if not default_spa_audio_set:
                track['properties']['default_track'] = True
                default_audio_set = True
            else:
                track['properties']['default_track'] = False

            processed_audio_tracks.append(track)
        elif lang == 'chi':
            track['properties']['language_ietf'] = 'zh-CN'
            track['properties']['track_name'] = 'Chinese'
            if not default_audio_set or not default_spa_audio_set:
                track['properties']['default_track'] = True
                default_audio_set = True
            else:
                track['properties']['default_track'] = False
            processed_audio_tracks.append(track)
        elif lang == 'kor':
            track['properties']['track_name'] = 'Korean'
            if not default_spa_audio_set or not default_audio_set:
                track['properties']['default_track'] = True
                default_audio_set = True
            else:
                track['properties']['default_track'] = False
            processed_audio_tracks.append(track)
        elif lang == 'eng':
            track['properties']['track_name'] = 'English'
            processed_audio_tracks.append(track)
            if not default_spa_audio_set and not default_audio_set:
                track['properties']['default_track'] = True
                default_audio_set = True
            else:
                track['properties']['default_track'] = False

    processed_subtitle_tracks = []
    default_subtitle_set = False
    found_forced_subtitle = False

    for track in subtitle_tracks:
        lang = track['properties'].get('language_ietf', track['properties'].get('language'))
        title = track['properties'].get('track_name', '').lower()
        forced = track['properties'].get('forced_track', False)
        if (lang == 'es-419' or 'lat' in title) and lang != 'hi-Latn':
            if 'forced' in title or forced:
                track['properties']['track_name'] = 'Spanish (Latin America) [Forced]'
                track['properties']['forced_track'] = True
                track['properties']['default_track'] = True
                track['properties']['language_ietf'] = 'es-419'
                if 'cr' in title: # add [CR] to the track name
                    track['properties']['track_name'] += ' [CR]'
                if 'ao' in title:
                    track['properties']['track_name'] += ' [AO]'
                processed_subtitle_tracks.insert(0, track)
                default_subtitle_set = True
                found_forced_subtitle = True
            else:
                track['properties']['track_name'] = 'Spanish (Latin America)'
                track['properties']['language_ietf'] = 'es-419'
                if not found_forced_subtitle:
                    if not default_spa_audio_set:
                        track['properties']['default_track'] = True
                        default_subtitle_set = True
                    else:
                        track['properties']['default_track'] = False
                else:
                    track['properties']['default_track'] = False
                if 'cr' in title: # add [CR] to the track name
                    track['properties']['track_name'] += ' [CR]'
                if 'ao' in title:
                    track['properties']['track_name'] += ' [AO]'
                if 'sdh' in title:
                    track['properties']['track_name'] += ' [SDH]'
                if 'cc' in title:
                    track['properties']['track_name'] += ' [CC]'
                if 'dub' in title:
                    track['properties']['track_name'] += ' [Dubtitle]'
                processed_subtitle_tracks.append(track)
        
    if not default_subtitle_set:
        for track in subtitle_tracks:
            lang = track['properties'].get('language')
            title = track['properties'].get('track_name', '').lower()
            if lang == 'spa' and not default_subtitle_set:
                track['properties']['track_name'] = 'Spanish'

                # Debe ser True si no se ha encontrado un subtítulo forzado o si no hay audio en español
                track['properties']['default_track'] = not found_forced_subtitle or not default_spa_audio_set
                default_subtitle_set = track['properties']['default_track']
                if 'sdh' in title:
                    track['properties']['track_name'] += ' [SDH]'
                if 'cc' in title:
                    track['properties']['track_name'] += ' [CC]'
                if 'dub' in title:
                    track['properties']['track_name'] += ' [Dubtitle]'
                processed_subtitle_tracks.append(track)
                break

    for track in subtitle_tracks:
        lang = track['properties'].get('language')
        forced = track['properties'].get('forced_track', False)
        title = track['properties'].get('track_name', '').lower()
        if lang == 'eng':
            if 'forced' in title or forced:
                track['properties']['track_name'] = 'English [Forced]'
                track['properties']['forced_track'] = True
            else:
                track['properties']['track_name'] = 'English'
            if not default_subtitle_set:
                track['properties']['default_track'] = True
            else:
                track['properties']['default_track'] = False
            if 'sdh' in title:
                track['properties']['track_name'] += ' [SDH]'
            if 'cc' in title:
                track['properties']['track_name'] += ' [CC]'
            if 'dub' in title:
                track['properties']['track_name'] += ' [Dubtitle]'
            processed_subtitle_tracks.append(track)

    return video_tracks + processed_audio_tracks + processed_subtitle_tracks

def mux_files(input_file, output_file, tracks):
    command = ['mkvmerge', '-o', output_file]
    track_order = []
    subtitle_tracks = []
    audio_tracks = []

    for track in tracks:
        track_id = track['id']
        lang = track['properties'].get('language_ietf', track['properties'].get('language'))
        title = track['properties'].get('track_name')
        default = 'yes' if track['properties'].get('default_track', False) else 'no'

        if track['type'] == 'subtitles':
            subtitle_tracks.append(str(track_id))
        
        # Agregar las pistas de audio
        if track['type'] == 'audio':
            audio_tracks.append(str(track_id))
        if track['type'] == 'video':
            lang = 'und'
            command.extend(['--language', f'{track_id}:{lang}'])
        else:
            command.extend(['--language', f'{track_id}:{lang}'])
        command.extend(['--default-track', f'{track_id}:{default}'])
        if title:
            # Si la pista es la de video, se le asigna '' como nombre
            if track['type'] == 'video':
                title = ''
            command.extend(['--track-name', f'{track_id}:{title}'])
        
        track_order.append(f"0:{str(track_id)}")

    # Agregar las pistas de audio al comando
    if audio_tracks:
        command.extend(['--audio-tracks', ','.join(audio_tracks)])

    # Agregar las pistas de subtítulos al comando

    if subtitle_tracks:
        command.extend(['--subtitle-tracks', ','.join(subtitle_tracks)])

    # Dejar el titulo del archivo de salida en blanco
    command.extend(['--title', ''])
    
    command.extend(['--track-order', ','.join(track_order)])
    command.append(input_file)

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error al ejecutar mkvmerge: {result.stdout}")
        sys.exit(1)
    print(f"Archivo muxeado guardado en {output_file}")

if __name__ == "__main__":
    input_path = args.input
    # Si no se especifica una carpeta de salida, se usará la carpeta de origen
    if args.output is None:
        output_path = input_path
    else:
        output_path = args.output

    if os.path.isdir(input_path):
        files = os.listdir(input_path)
        files = [f for f in files if f.endswith('.mkv')]
        files.sort()
        for file in files:
            input_file = os.path.join(input_path, file)
            # Agregar _muxed al nombre del archivo de salida
            output_file = os.path.join(output_path, f"{os.path.splitext(file)[0]}_muxed.mkv")
            metadata = get_mkv_metadata(input_file)
            processed_tracks = process_tracks(metadata)
            mux_files(input_file, output_file, processed_tracks)
            if args.delete_after:
                os.remove(input_file)
    else:
        metadata = get_mkv_metadata(input_path)
        processed_tracks = process_tracks(metadata)
        mux_files(input_path, output_path, processed_tracks)