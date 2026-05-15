import zipfile, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
FOLDERS = ["quark_qq_inject", "quark_daily_sign"]


def make_zip(folder: str):
    zipname = os.path.join(BASE, f"{folder}.zip")
    path = os.path.join(BASE, folder)
    if not os.path.isdir(path):
        print(f"!! {folder} not found, skip")
        return
    with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED) as z:
        # 写入顶层目录条目
        z.write(path, folder + "/")
        # 写入子目录 + 文件
        for root, dirs, files in os.walk(path):
            for name in dirs:
                arc = os.path.relpath(os.path.join(root, name), BASE) + "/"
                z.write(os.path.join(root, name), arc)
            for name in files:
                arc = os.path.relpath(os.path.join(root, name), BASE)
                z.write(os.path.join(root, name), arc)
    print(f"OK  {zipname}")


if __name__ == "__main__":
    for f in FOLDERS:
        make_zip(f)
    print("Done")
