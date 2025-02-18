# Device42 Export Auditlog

## Prerequisites

Ensure you have the following installed on your system:

- Python (version 3.x recommended)
- pip (Python package manager)

You can check your Python and pip installation by running:

```sh
python --version
pip --version
```

## Setting Up a Virtual Environment

1. Navigate to your project directory:

   ```sh
   cd /path/to/your/project
   ```

2. Create a virtual environment:

   ```sh
   python -m venv venv
   ```

3. Activate the virtual environment:

   - **Windows**:
     ```sh
     venv\Scripts\activate
     ```
   - **Mac/Linux**:
     ```sh
     source venv/bin/activate
     ```

4. Verify the virtual environment is active (your terminal should show `(venv)` at the beginning of the line).

## Installing Dependencies

If your project has dependencies listed in a `requirements.txt` file, install them by running:

```sh
pip install -r requirements.txt
```

## Running the Python Script

To execute the script, run:

```sh
python d42_auditlog_export_script.py
```

Replace `d42_auditlog_export_script.py` with the actual filename if different.

## Configuration

Ensure you have the necessary configurations set in the script:

- Device42 API URL
- Authentication credentials (username and password)
- Interval data filter

Example configuration variables setup:
```sh
D42_HOST = "192.168.1.1"
D42_USERNAME = "admin"
D42_PASSWORD = "your-password"
QUERY_INTERVAL_DAYS = 60
```

## Deactivating the Virtual Environment

Once you're done, deactivate the virtual environment by running:

```sh
deactivate
```

## Additional Notes

- If `venv` is not found, ensure Python is installed correctly and available in your system's PATH.
- For a fresh installation of dependencies, delete the `venv` folder and repeat the setup steps.

## Troubleshooting

- If you encounter `ModuleNotFoundError`, make sure the virtual environment is activated and dependencies are installed.
- If you have multiple Python versions installed, use `python3` instead of `python`.

For further assistance, refer to the official Python documentation: [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html).

