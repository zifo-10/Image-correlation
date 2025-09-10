def read_srt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        print(content)


# Example usage
# srt_file = "../../V4-caption.srt"
# read_and_print_file(srt_file)
