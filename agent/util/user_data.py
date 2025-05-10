from dataclasses import dataclass
from typing import Optional

@dataclass
class UserData:
    """Class to store user information for job applications."""
    first_name: str = "Prama"
    last_name: str = "Yudhistira"
    email: str = "pyudhistira3@gatech.edu"
    phone: Optional[str] = "4705294451"
    linkedin_url: Optional[str] = "https://linkedin.com/in/pramayudhistira"
    github_url: Optional[str] = "https://github.com/PramaYudhistira"
    portfolio_url: Optional[str] = "https://www.prama.dev"
    current_company: Optional[str] = "AMD"
    current_title: Optional[str] = "Software Engineer"
    years_of_experience: Optional[int] = 1
    location: Optional[str] = "San Francisco, CA"
    visa_sponsorship: Optional[bool] = False
    notice_period: Optional[str] = "2 weeks" 