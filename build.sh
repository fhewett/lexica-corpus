VENV='lexica_corpus'

echo "Preparing Python environment..."
virtualenv -p python3 $VENV
source $VENV/bin/activate
pip install -r requirements.txt

echo "Running script to create corpus..."
python parse_lexica.py
