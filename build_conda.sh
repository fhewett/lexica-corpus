VENV='lexica_corpus'

echo "Preparing Conda environment..."
conda env create --name $VENV --file environment.yml

echo "Entering environment..."
eval "$(conda shell.bash hook)"
conda activate lexica_corpus

echo "Running script to create corpus..."
python parse_lexica.py
