import subprocess

def extract_frames_from_m3u8(m3u8_url, num_frames, output_path):
    # 构建 filter_complex 参数
    filter_complex = f"[0:v]trim=start=9*60:duration={num_frames*20},setpts=PTS-STARTPTS,fps=1/20[outv]"

    # 构建输出参数
    output_args = f"-map [outv] -q:v 2 {output_path}/frame_%d.jpg"
    print(f'ffmpeg -i {m3u8_url} -filter_complex {filter_complex} {output_args}')
    # 执行截图命令
    command = ['ffmpeg', '-i', m3u8_url, '-filter_complex', filter_complex, output_args]
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        print(f'Successfully extracted {num_frames} frames.')
    except Exception as e:
        print(f'Error extracting frames from m3u8: {str(e)}')

# 示例用法
m3u8_url = 'https://vip.lz-cdn12.com/20230607/7937_96e2ae72/index.m3u8'
num_frames = 4
output_path = './output'
extract_frames_from_m3u8(m3u8_url, num_frames, output_path)

# ffmpeg -ss 00:09:00 -i https://vip.lz-cdn12.com/20230607/7937_96e2ae72/index.m3u8 -vf "select='not(mod(n\,1200))',setpts=N/FRAME_RATE/TB" -vframes 4 out/output%d.jpg
