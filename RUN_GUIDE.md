# AI Sleep Wellness Assistant — Run Guide

## 1. Open the project
Open this folder in VS Code.

## 2. Create a virtual environment
```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Start the application
```bash
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal.

## 5. Train/update the model
If the project contains the training script:
```bash
python model/train_model.py
```

## 6. Test the model
If the project contains the test script:
```bash
python model/test_model.py
```

### Project flow
User Input → Validation → ML Prediction → Sleep/Welfare Scores → Recommendations → SQLite History → Dashboard/Analytics

> This is an educational wellness prototype, not a medical diagnostic tool.
