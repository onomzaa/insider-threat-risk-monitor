# Generate the project PowerPoint

This repository includes a Python script that creates a 12-slide editable PowerPoint from the research project content.

## Requirements
- Python 3.10+
- `python-pptx`

## Windows / PowerShell
From the repository root:

```powershell
python -m pip install python-pptx
python scripts/generate_presentation.py
```

Output:
`presentation/Insider_Threat_Risk_Monitor.pptx`

## Before presenting
- Replace group/institution placeholders on slide 1.
- Add a real dashboard screenshot to slides 5 or 7.
- Add actual evaluation metrics and test results to slide 9.
- Review speaker notes and rehearse the guided synthetic demo.
- Keep the synthetic-data and prototype limitations explicit.

The generator uses editable PowerPoint text and shapes. It does not fabricate evaluation metrics or real-world performance claims.
