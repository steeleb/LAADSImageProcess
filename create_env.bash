python3 -m venv env
source env/bin/activate
python3 -m pip install numpy matplotlib pandas xarray
python3 -m pip freeze > requirements.txt

#optional
pip install --upgrade pip