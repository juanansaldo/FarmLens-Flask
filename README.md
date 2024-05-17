# FarmLens: Flask
This is the FarmLens repository for the video inference flask app hosted on AWS. This codebase leverages a custom [YOLOv9](https://github.com/WongKinYiu/yolov9) object detection model for strawberry ripeness detection.

A virtual environment is necessary to run this project. To create a virtual environment in your current directory: <br>
python -m venv <environment_name>

To activate environment: <br>
MacOS: source <environment_name>/bin/activate <br>
Windows: .\\<environment_name>\Scripts\activate

Once the environment is activated, install the packages. <br>
pip install -r requirements.txt

To run the flask app locally: <br>
1. Go to the directory with the api.py script
2. Create environment variables <br>

MacOS: <br>
export FLASK_APP="api.py" <br>
export FLASK_DEBUG="1" <br>
export ROBOFLOW_API_KEY="{API_KEY}" <br>
export ROBOFLOW_MODEL_ID="{MODEL_ID}" <br>

Windows: <br>
$env:FLASK_APP="api.py" <br>
$env:FLASK_DEBUG="1" <br>
$env:ROBOFLOW_API_KEY="{API_KEY}" <br>
$env:ROBOFLOW_MODEL_ID="{MODEL_ID}" <br>

3. Run the flask app <br>
- flask run <br>
- flask run --host=0.0.0.0 --port=5000 (Optional. Accepts requests from your entire network)

[FarmLens-ML repo](https://github.com/juanansaldo/FarmLens-ML) <br>
[FarmLens-Unity repo](https://github.com/novicecodersnail/farmlens)
