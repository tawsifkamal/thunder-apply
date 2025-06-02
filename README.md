# Thunder Apply 🚀

**One Click Apply → Watch AI apply to jobs for you → Relax**

Thunder Apply is an intelligent job application automation tool that uses web scraping and form filling to automatically apply to job postings. Built with Python, Selenium, and LangChain.

## ✨ Features

- **Automated Form Filling**: Intelligently detects and fills job application forms
- **Smart Field Mapping**: Automatically maps your profile data to form fields
- **Retry Logic**: Robust error handling with configurable retry mechanisms
- **Multi-Job Support**: Apply to multiple jobs from a list of URLs
- **Configurable**: Extensive configuration options for different use cases
- **Logging**: Comprehensive logging for debugging and monitoring
- **Headless Mode**: Run in background without opening browser windows

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Chrome browser
- ChromeDriver (automatically managed by Selenium)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/tawsifkamal/thunder-apply.git
cd thunder-apply
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your profile in `profile.json` (see example below)

4. Run the application:
```bash
python thunder_apply.py --url "https://example-job-posting.com"
```

## 📋 Configuration

### Profile Configuration (`profile.json`)

Update the `profile.json` file with your personal information:

```json
{
  "first_name": "Your Name",
  "last_name": "Your Last Name",
  "email": "your.email@example.com",
  "phone_number": "123-456-7890",
  "location": {
    "full_location": "City, State, Country",
    "city": "Your City",
    "state": "Your State",
    "country": "Your Country"
  },
  "resume_path": "./your_resume.pdf",
  "experiences": [...],
  "skills": {...}
}
```

### Application Configuration (`config.json`)

Customize the application behavior:

```json
{
  "webdriver": {
    "headless": true,
    "implicit_wait": 5,
    "page_load_timeout": 30
  },
  "automation": {
    "max_retries": 3,
    "retry_delay": 2,
    "form_fill_delay": 0.5
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

## 🎯 Usage

### Apply to a Single Job

```bash
python thunder_apply.py --url "https://company.com/job-posting"
```

### Apply to Multiple Jobs

Create a file with job URLs (one per line):

```bash
echo "https://company1.com/job1" > jobs.txt
echo "https://company2.com/job2" >> jobs.txt
python thunder_apply.py --urls-file jobs.txt
```

### Extract Page Structure (for debugging)

```bash
python thunder_apply.py --url "https://company.com/job-posting" --extract-only
```

### Command Line Options

- `--config`: Path to configuration file
- `--profile`: Path to profile JSON file (default: profile.json)
- `--url`: Single job URL to apply to
- `--urls-file`: File containing list of job URLs
- `--extract-only`: Only extract page structure (for debugging)
- `--headless`: Run in headless mode
- `--verbose`: Enable verbose logging

## 🏗️ Architecture

The application is structured into several modules:

- **`thunder_apply.py`**: Main application entry point
- **`selenium_driver.py`**: Core web automation and DOM extraction
- **`automation_utils.py`**: Utility functions for common automation tasks
- **`config.py`**: Configuration management
- **`profile.json`**: User profile data
- **`config.json`**: Application configuration

### Key Components

1. **SimplifiedDOMExtractor**: Handles web page loading and DOM extraction
2. **FormFieldMapper**: Intelligently maps profile data to form fields
3. **ElementInteractor**: Provides safe element interaction with retry logic
4. **JobApplicationHelper**: Job-specific automation utilities
5. **RetryHandler**: Configurable retry logic for robust automation

## 🔧 Advanced Usage

### Custom Field Mapping

For sites with non-standard forms, you can provide custom field mappings:

```python
custom_mapping = {
    "first_name": {"id": "fname", "type": "input"},
    "last_name": {"id": "lname", "type": "input"},
    "email": {"id": "email_address", "type": "input"},
    "resume": {"id": "resume_upload", "type": "file"}
}

app.apply_to_job(url, custom_mapping)
```

### Programmatic Usage

```python
from thunder_apply import ThunderApply

with ThunderApply("config.json") as app:
    success = app.apply_to_job("https://company.com/job")
    if success:
        print("Application submitted successfully!")
```

## 🛡️ Error Handling

The application includes comprehensive error handling:

- **Retry Logic**: Automatically retries failed operations
- **Graceful Degradation**: Falls back to basic autofill if smart mapping fails
- **Detailed Logging**: Comprehensive logs for debugging
- **Exception Handling**: Proper error handling throughout the application

## 📊 Logging

Logs include:
- Page loading status
- Form field detection and mapping
- Application submission results
- Error details and stack traces

Configure logging level in `config.json` or use `--verbose` flag.

## ⚠️ Important Notes

- **Respect Rate Limits**: Don't overwhelm job sites with requests
- **Review Applications**: Always review applications before submission
- **Terms of Service**: Ensure compliance with job site terms of service
- **Resume Quality**: Keep your resume and profile data up to date

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational and personal use. Please respect the terms of service of job posting websites.

## 🐛 Troubleshooting

### Common Issues

1. **ChromeDriver Issues**: Ensure Chrome browser is installed and up to date
2. **Element Not Found**: Use `--extract-only` to debug page structure
3. **Timeout Errors**: Increase timeout values in configuration
4. **Form Not Detected**: Check if the page requires login or has anti-bot measures

### Debug Mode

Run with verbose logging to see detailed execution information:

```bash
python thunder_apply.py --url "https://example.com" --verbose
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue on GitHub with detailed information

---

**Happy Job Hunting! 🎯**

