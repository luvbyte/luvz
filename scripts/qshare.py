from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from contextlib import asynccontextmanager
from pathlib import Path
import mimetypes
import uvicorn

from luvz import ZScript, Arg, run_script


script = ZScript()

SHARED_DIR = Path("./").resolve()
HOST = "localhost"
PORT = 8080


@asynccontextmanager
async def lifespan(app: FastAPI):
  script.scr.print_panel(f"[bold cyan]ROOT[/bold cyan]: [magenta]{SHARED_DIR}[/magenta]\n[bold cyan]HOST[/bold cyan]: [magenta]{HOST}[/magenta]\n[bold cyan]PORT[/bold cyan]: [magenta]{PORT}[/magenta]\n[bold cyan]URL [/bold cyan]: [link=http://{HOST}:{PORT}]http://{HOST}:{PORT}[/link]", title="STARTED", subtitle="Press ([red]Ctrl + C[/red]) to Stop")
  yield

app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def index():
  return await list_directory("")

@app.get("/browse/{path:path}", response_class=HTMLResponse)
async def list_directory(path: str):
  """
  Browse directory with TailwindCSS UI + search bar.
  """
  target_dir = (SHARED_DIR / path).resolve()

  if not target_dir.exists() or not target_dir.is_dir() or (
    SHARED_DIR not in target_dir.parents and target_dir != SHARED_DIR
  ):
    raise HTTPException(status_code=404, detail="Directory not found")

  # Build directory listing rows
  rows_html = ""
  if target_dir != SHARED_DIR:
    parent_rel = str(Path(path).parent)
    rows_html += f"""
    <tr class='hover:bg-gray-300 bg-gray-200'>
      <td class='p-2'><a class='text-blue-500 hover:underline' href='/browse/{parent_rel}'>⬅️ Back</a></td>
      <td></td>
    </tr>
    """
  for item in sorted(target_dir.iterdir()):
    rel_path = (Path(path) / item.name).as_posix()
    if item.is_dir():
      rows_html += f"""
      <tr class='hover:bg-gray-100 file-row'>
        <td class='p-2'>📁 <a class='text-blue-600 hover:underline' href='/browse/{rel_path}'>{item.name}/</a></td>
        <td class='text-gray-400 p-2'>Directory</td>
      </tr>
      """
    else:
      rows_html += f"""
      <tr class='hover:bg-gray-100 file-row'>
        <td class='p-2'>📄 <a class='text-blue-600 hover:underline' href='/download/{rel_path}' download>{item.name}</a></td>
        <td class='text-gray-400 p-2'>{round(item.stat().st_size/1024,1)} KB</td>
      </tr>
      """

  html = f"""
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <title>File Browser</title>
  </head>
  <body class="bg-gray-50 text-gray-900">
    <div class="p-3 bg-gradient-to-b from-orange-200 to-orange-400 font-bold">QShare</div>
    <div class="p-2 bg-white/60 font-bold shadow-lg md:text-2xl">📂 /{path}</div>
    <div class="container mx-auto p-6">
      <!-- Search bar -->
      <div class="mb-4">
        <input type="text" id="searchInput" placeholder="Search files..." 
          class="w-full p-2 border shadow-sm focus:border-orange-400 focus:outline-none"
          onkeyup="filterFiles()">
      </div>

      <table class="table-auto w-full border-collapse border border-gray-200 shadow-sm rounded">
        <thead class="bg-orange-200">
          <tr>
            <th class="text-left p-2">Name</th>
            <th class="text-left p-2">Size</th>
          </tr>
        </thead>
        <tbody id="fileTableBody">
          {rows_html}
        </tbody>
      </table>
    </div>

    <script>
    function filterFiles() {{
      const input = document.getElementById('searchInput');
      const filter = input.value.toLowerCase();
      const rows = document.querySelectorAll('#fileTableBody .file-row');
      rows.forEach(row => {{
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
      }});
    }}
    </script>
  </body>
  </html>
  """
  return HTMLResponse(content=html)


@app.get("/download/{path:path}")
async def download_file(path: str):
  file_path = (SHARED_DIR / path).resolve()

  if not file_path.exists() or not file_path.is_file() or SHARED_DIR not in file_path.parents:
    raise HTTPException(status_code=404, detail="File not found")

  # Guess MIME type correctly
  mime_type, _ = mimetypes.guess_type(file_path)
  return FileResponse(
    path=file_path,
    filename=file_path.name,   # Ensures the original filename
    media_type=mime_type or 'application/octet-stream'  # Fallback
  )

@script.on("serve", short="Start server")
def serve(
  bind: Arg.Path() = "",
  host: str = "localhost",
  port: int = 8080,
  verbose: Arg("-v", action="store_true", help="Enable verbose") = False,
):
  global HOST, PORT, SHARED_DIR
  HOST = host
  PORT = port
  
  SHARED_DIR = Path(bind).resolve()
  uvicorn.run(app, host=HOST, port=PORT, log_level="info" if verbose else "critical")

if __name__ == "__main__":
  run_script(script)

