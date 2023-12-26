import ast
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from typing import List
import Inference3
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/output", StaticFiles(directory="output"), name="output")

log_filename = "history.log"  # 로그 파일 이름
results_data = []

def log_results(results):
    with open(log_filename, "a") as log_file:
        for result in results:
            log_file.write(f"{result}\n")

@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload_form.html", {"request": request})

def save_results_to_csv(results, filename="results.csv"):
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)

@app.post("/upload/")
async def upload_images(files: List[UploadFile] = File(...)):
    global results_data
    results = []

    for file in files:
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())  # 비동기 파일 읽기

        # Inference3 실행
        args = Inference3.get_config()
        args.img_path = file_location
        leaf_area = Inference3.process_image(file_location, args)

        output_image_path = os.path.join('output', os.path.splitext(file.filename)[0] + '.jpg')
        output_image_url = f'/output/{os.path.basename(output_image_path)}'

        results.append({"filename": file.filename, "leaf_area": leaf_area, "output_image_url": output_image_url})

    save_results_to_csv(results)
    results_data.append(results)
    log_results(results)  # 결과 로깅

    return results

@app.get("/download_csv/")
async def download_csv():
    return FileResponse("results.csv", media_type='application/octet-stream', filename="results.csv")

@app.get("/results/")
async def get_results():
    global results_data
    return results_data

@app.get("/history/", response_class=HTMLResponse)
async def view_history(request: Request):
    with open("history.log", "r") as log_file:
        history_data = [ast.literal_eval(line) for line in log_file.readlines()]
    return templates.TemplateResponse("history_page.html", {"request": request, "history": history_data})

@app.get("/view-results/", response_class=HTMLResponse)
async def view_results(request: Request):
    return templates.TemplateResponse("results_page.html", {"request": request})

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app="server:app",
#                     host="0.0.0.0",
#                     port=8001,
#                     reload=True)

