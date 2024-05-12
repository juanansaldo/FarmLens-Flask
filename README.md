# FarmLens: Flask
This is the FarmLens repository for the video inference flask app hosted on AWS. This codebase leverages a custom [YOLOv9](https://github.com/WongKinYiu/yolov9) object detection model for strawberry ripeness detection.

A virtual environment is necessary to run this project. To create a virtual environment in your current directory:
python -m venv <environment_name>

To activate environment:
MacOS: source <environment_name>/bin/activate <br>
Windows: .\<environment_name>\Scripts\activate

Once the environment is activated, install the packages.
pip install -r requirements.txt
