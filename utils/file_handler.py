import os
from werkzeug.utils import secure_filename


MAX_FILE_SIZE=5 * 1024 * 1024   


MAGIC_BYTES={
    "jpg":[(0,b"\xff\xd8\xff")],
    "jpeg":[(0,b"\xff\xd8\xff")],
    "png":[(0,b"\x89PNG")],
    "pdf":[(0,b"%PDF")],
}

ALLOWED_EXTENSIONS=set(MAGIC_BYTES.keys())


def allowed_extension(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def check_magic_bytes(file_stream,extension: str) -> bool:
    
    checks=MAGIC_BYTES.get(extension.lower(), [])
    if not checks:
        return False


    file_stream.seek(0)
    header=file_stream.read(16)
    file_stream.seek(0)

    for offset,magic in checks:
        if header[offset: offset + len(magic)]==magic:
            return True
        
    return False


def validate_and_save(file,upload_folder: str) -> tuple[bool,str,str | None]:
   
    if not file or file.filename=="":
        return True,"", None    

    filename=secure_filename(file.filename)
    extension=filename.rsplit(".", 1)[1].lower() if "." in filename else ""

    if not allowed_extension(filename):
        return False,"File type not allowed. Upload PNG, JPG or PDF only.", None

    
    file.seek(0, 2)                 
    size=file.tell()
    file.seek(0)                    

    if size > MAX_FILE_SIZE:
        return False,f"File too large. Maximum allowed size is 5 MB.",None

    if not check_magic_bytes(file, extension):
        return False, "File content does not match its extension.",None

    os.makedirs(upload_folder,exist_ok=True)
    save_path=os.path.join(upload_folder,filename)
    file.save(save_path)

    return True,"",save_path