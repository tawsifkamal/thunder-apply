"use client"

import FileUploader from "./FileUploader";

import { useState } from 'react';

export default function Form() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    phoneNumber: '',
    email: '',
    address: {
      street: '',
      city: '',
      state: '',
      country: '',
      postalCode: '',
    },
    gpa: '',
    graduationDate: '',
    canWorkInUS: '',
    requiresVisaSponsorship: '',
    gender: '',
    racialBackground: '',
    veteranStatus: '',
    disabilityStatus: '',
    locationPreferences: '',
    password: '',
    resume: null,
    workExperience: [],
    education: [],
    languages: [],
    skills: '',
    websites: [],
    url: '',
  });

  // Dynamic fields toggle
  const [showWorkExperience, setShowWorkExperience] = useState(false);
  const [showEducation, setShowEducation] = useState(false);
  const [showLanguages, setShowLanguages] = useState(false);
  const [showSkills, setShowSkills] = useState(false);
  const [showWebsites, setShowWebsites] = useState(false);

  const handleChange = (e, index=null) => {
    const { name, value, files } = e.target;
    if (name === 'resume') {
      setFormData({ ...formData, [name]: files[0] });
    } else if (name.includes('address')) {
      setFormData({
        ...formData,
        address: { ...formData.address, [name.split('.')[1]]: value },
      });
    } else if (name.includes('workExperience')) {
      const updatedWorkExperience = [...formData.workExperience];
      updatedWorkExperience[index] = {
        ...updatedWorkExperience[index],
        [name.split('.')[1]]: value,
      };
      setFormData({
        ...formData,
        workExperience: updatedWorkExperience,
      });
    } else if (name.includes('education')) {
      const updatedEducation = [...formData.education];
      updatedEducation[index] = {
        ...updatedEducation[index],
        [name.split('.')[1]]: value,
      };
      setFormData({
        ...formData,
        education: updatedEducation,
      });
    } else if (name.includes('languages')) {
      const updatedLanguages = [...formData.languages];
      updatedLanguages[index] = {
        ...updatedLanguages[index],
        [name.split('.')[1]]: value,
      };
      setFormData({
        ...formData,
        languages: updatedLanguages,
      });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Convert form data to JSON format
    const jsonData = JSON.stringify(formData);

    // Send JSON data to the server-side API
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonData,
    });

    if (response.ok) {
      alert('Form submitted successfully!');
    } else {
      alert('Form submission failed.');
    }
  };

  // Function to add new work experience
  const addWorkExperience = () => {
    setFormData({
      ...formData,
      workExperience: [...formData.workExperience, {jobTitle: '', company: '', location: '', startDate: '', endDate: '', currentlyWorking: false, roleDescription: ''}]
    });
    setShowWorkExperience(true)
  };

  // Function to remove new work experience
  const removeWorkExperience = () => {
    setFormData({
      ...formData,
      workExperience: [{jobTitle: '', company: '', location: '', startDate: '', endDate: '', currentlyWorking: false, roleDescription: ''}]
    });
    setShowWorkExperience(false)
  };

  // Function to add new education
  const addEducation = () => {
    setFormData({
      ...formData,
      education: [...formData.education, { school: '', degree: '', fieldOfStudy: '', startDate: '', endDate: '' }]
    });
    setShowEducation(true)
  };
  // Function to remove new education
  const removeEducation = () => {
    setFormData({
      ...formData,
      education: [{ school: '', degree: '', fieldOfStudy: '', startDate: '', endDate: '' }]
    });
    setShowEducation(false)
  };

  // Function to add new language
  const addLanguage = () => {
    setFormData({
      ...formData,
      languages: [...formData.languages, { language: '', proficiency: '' }]
    });
    setShowLanguages(true)
  };
  // Function to remove new language
  const removeLanguage = () => {
    setFormData({
      ...formData,
      languages: [{ language: '', proficiency: '' }]
    });
    setShowLanguages(false)
  };

  // Function to add website
  const addWebsite = () => {
    setFormData({
      ...formData,
      websites: [...formData.websites, '']
    });
    setShowWebsites(true)
  };
  // Function to remove website
  const removeWebsite = () => {
    setFormData({
      ...formData,
      websites: ['']
    });
    setShowWebsites(false)
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>First Name:</label>
        <input type="text" name="firstName" value={formData.firstName} onChange={handleChange} required />
      </div>

      <div>
        <label>Last Name:</label>
        <input type="text" name="lastName" value={formData.lastName} onChange={handleChange} required />
      </div>

      <div>
        <label>Phone Number:</label>
        <input type="text" name="phoneNumber" value={formData.phoneNumber} onChange={handleChange} required />
      </div>

      <div>
        <label>Email:</label>
        <input type="email" name="email" value={formData.email} onChange={handleChange} required />
      </div>

      <div>
        <label>Street Address:</label>
        <input type="text" name="address.street" value={formData.address.street} onChange={handleChange} required />
      </div>

      <div>
        <label>City:</label>
        <input type="text" name="address.city" value={formData.address.city} onChange={handleChange} required />
      </div>

      <div>
        <label>State:</label>
        <select name="address.state" value={formData.address.state} onChange={handleChange} required>
          {/* List of US States */}
          <option value="">Select State</option>
          <option value="AL">Alabama</option>
          <option value="AK">Alaska</option>
          <option value="AZ">Arizona</option>
          <option value="AR">Arkansas</option>
          <option value="CA">California</option>
          <option value="CO">Colorado</option>
          <option value="CT">Connecticut</option>
          <option value="DE">Delaware</option>
          <option value="FL">Florida</option>
          <option value="GA">Georgia</option>
          <option value="HI">Hawaii</option>
          <option value="ID">Idaho</option>
          <option value="IL">Illinois</option>
          <option value="IN">Indiana</option>
          <option value="IA">Iowa</option>
          <option value="KS">Kansas</option>
          <option value="KY">Kentucky</option>
          <option value="LA">Louisiana</option>
          <option value="ME">Maine</option>
          <option value="MD">Maryland</option>
          <option value="MA">Massachusetts</option>
          <option value="MI">Michigan</option>
          <option value="MN">Minnesota</option>
          <option value="MS">Mississippi</option>
          <option value="MO">Missouri</option>
          <option value="MT">Montana</option>
          <option value="NE">Nebraska</option>
          <option value="NV">Nevada</option>
          <option value="NH">New Hampshire</option>
          <option value="NJ">New Jersey</option>
          <option value="NM">New Mexico</option>
          <option value="NY">New York</option>
          <option value="NC">North Carolina</option>
          <option value="ND">North Dakota</option>
          <option value="OH">Ohio</option>
          <option value="OK">Oklahoma</option>
          <option value="OR">Oregon</option>
          <option value="PA">Pennsylvania</option>
          <option value="RI">Rhode Island</option>
          <option value="SC">South Carolina</option>
          <option value="SD">South Dakota</option>
          <option value="TN">Tennessee</option>
          <option value="TX">Texas</option>
          <option value="UT">Utah</option>
          <option value="VT">Vermont</option>
          <option value="VA">Virginia</option>
          <option value="WA">Washington</option>
          <option value="WV">West Virginia</option>
          <option value="WI">Wisconsin</option>
          <option value="WY">Wyoming</option>
        </select>
      </div>

      <div>
        <label>Country:</label>
        <select name="address.country" value={formData.address.country} onChange={handleChange} required>
          {/* List of Countries */}
          <option value="">Select Country</option>
          <option value="USA">United States</option>
          <option value="CAN">Canada</option>
          {/* Add other countries here */}
        </select>
      </div>

      <div>
        <label>Postal Code:</label>
        <input type="text" name="address.postalCode" value={formData.address.postalCode} onChange={handleChange} required />
      </div>

      <div>
        <label>GPA:</label>
        <input type="text" name="gpa" value={formData.gpa} onChange={handleChange} required />
      </div>

      <div>
        <label>Graduation Date:</label>
        <input type="month" name="graduationDate" value={formData.graduationDate} onChange={handleChange} required />
      </div>

      <div>
        <label>Can you legally work in the USA?</label>
        <select name="canWorkInUS" value={formData.canWorkInUS} onChange={handleChange} required>
          <option value="">Select</option>
          <option value="Yes">Yes</option>
          <option value="No">No</option>
        </select>
      </div>

      <div>
        <label>Do you require visa sponsorship?</label>
        <select name="requiresVisaSponsorship" value={formData.requiresVisaSponsorship} onChange={handleChange} required>
          <option value="">Select</option>
          <option value="Yes">Yes</option>
          <option value="No">No</option>
        </select>
      </div>

      <div>
        <label>Gender:</label>
        <select name="gender" value={formData.gender} onChange={handleChange} required>
          <option value="">Select</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Prefer not to answer">Prefer not to answer</option>
        </select>
      </div>

      <div>
        <label>Racial Background:</label>
        <select name="racialBackground" value={formData.racialBackground} onChange={handleChange} required>
          <option value="">Select</option>
          <option value="American Indian or Alaska Native">American Indian or Alaska Native</option>
          <option value="Asian">Asian</option>
          <option value="Black or African American">Black or African American</option>
          <option value="Hispanic or Latino">Hispanic or Latino</option>
          <option value="Native Hawaiian or Other Pacific Islander">Native Hawaiian or Other Pacific Islander</option>
          <option value="Two or More Races (Not Hispanic or Latino)">Two or More Races (Not Hispanic or Latino)</option>
          <option value="White">White</option>
        </select>
      </div>

      <div>
        <label>Veteran Status:</label>
        <select name="veteranStatus" value={formData.veteranStatus} onChange={handleChange} required>
          <option value="">Select</option>
          <option value="Protected Veteran">I identify as one or more of the classifications of Protected Veterans</option>
          <option value="Veteran">I identify as a Veteran, just not a Protected Veteran</option>
          <option value="Not a Veteran">I am not a Veteran</option>
          <option value="Prefer not to say">I do not wish to self-identify</option>
        </select>
      </div>

      <div>
        <label>Disability Status:</label>
        <select name="disabilityStatus" value={formData.disabilityStatus} onChange={handleChange} required>
          <option value="">Select</option>
          <option value="Yes">Yes</option>
          <option value="No">No</option>
          <option value="Prefer not to answer">Prefer not to answer</option>
        </select>
      </div>

      <div>
        <label>City Location Preferences:</label>
        <input type="text" name="locationPreferences" value={formData.locationPreferences} onChange={handleChange} required />
      </div>

      <div>
        <label>Password:</label>
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          required
          pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9])(?=.*[A-Za-z]).{8,}$"
          title="Password must contain a lowercase character, an uppercase character, a special character, a minimum of 8 characters, a numeric character, and an alphabetic character."
        />
      </div>

      {/* Resume Upload */}
      <div>
        <label>Upload Resume:</label>
        <input type="file" name="resume" accept=".pdf,.docx" onChange={handleChange} required />
      </div>

      {/* Work Experience Section */}
      <div>
        <button type="button" onClick={addWorkExperience}>Add Work Experience</button>
        {showWorkExperience && (
          <>
            {formData.workExperience.map((exp, index) => (
              <div key={index}>
                <label>Job Title:</label>
                <input type="text" name={`workExperience.jobTitle`} value={exp.jobTitle} onChange={(e) => handleChange(e, index)} required />

                <label>Company:</label>
                <input type="text" name={`workExperience.company`} value={exp.company} onChange={(e) => handleChange(e, index)} required />

                <label>Location:</label>
                <input type="text" name={`workExperience.location`} value={exp.location} onChange={(e) => handleChange(e, index)} />

                <label>Start Date:</label>
                <input type="month" name={`workExperience.startDate`} value={exp.startDate} onChange={(e) => handleChange(e, index)} required />

                <label>End Date:</label>
                <input type="month" name={`workExperience.endDate`} value={exp.endDate} onChange={(e) => handleChange(e, index)} />

                <label>
                  <input type="checkbox" name={`workExperience.currentlyWorking`} value={exp.currentlyWorking} onChange={(e) => handleChange(e, index)} /> I currently work here
                </label>

                <label>Role Description:</label>
                <textarea name={`workExperience.roleDescription`} value={exp.roleDescription} onChange={(e) => handleChange(e, index)} />
              </div>
            ))}
            <button type="button" onClick={removeWorkExperience}>Remove All Work Experience</button>
          </>
        )}
      </div>

      {/* Education Section */}
      <div>
        <button type="button" onClick={addEducation}>Add Education</button>
        {showEducation && (
          <>
            {formData.education.map((edu, index) => (
              <div key={index}>
                <label>School/University:</label>
                <input type="text" name={`education.school`} value={edu.school} onChange={(e) => handleChange(e, index)} required />

                <label>Degree:</label>
                <select name={`education.degree`} onChange={(e) => handleChange(e, index)} required>
                  <option value="GED">GED</option>
                  <option value="High School">High School</option>
                  <option value="Associates">Associates</option>
                  <option value="Bachelors">Bachelors</option>
                  <option value="Masters">Masters</option>
                  <option value="Doctorate">Doctorate</option>
                </select>

                <label>Field of Study:</label>
                <input type="text" name={`education.fieldOfStudy`} value={edu.fieldOfStudy} onChange={(e) => handleChange(e, index)} required />

                <label>Start Date:</label>
                <input type="month" name={`education.startDate`} value={edu.startDate} onChange={(e) => handleChange(e, index)} required />

                <label>End Date:</label>
                <input type="month" name={`education.endDate`} value={edu.endDate} onChange={(e) => handleChange(e, index)} required />
              </div>
            ))}
            <button type="button" onClick={removeEducation}>Remove All Education</button>
          </>
        )}
      </div>

      {/* Languages Section */}
      <div>
        <button type="button" onClick={addLanguage}>Add Languages</button>
        {showLanguages && (
          <>
            {formData.languages.map((lang, index) => (
              <div key={index}>
                <label>Language:</label>
                <input type="text" name={`languages.language`} value={lang.language} onChange={(e) => handleChange(e, index)} required />

                <label>Proficiency:</label>
                <select name={`languages.proficiency`} onChange={(e) => handleChange(e, index)} required>
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                  <option value="Fluent">Fluent</option>
                </select>
              </div>
            ))}
            <button type="button" onClick={removeLanguage}>Remove All Languages</button>
          </>
        )}
      </div>

      {/* Skills Section */}
      <div>
        <button type="button" onClick={() => setShowSkills(true)}>Add Skills</button>
        {showSkills && (
          <div>
            <label>Skills (separated by commas):</label>
            <textarea name="skills" required onChange={handleChange}></textarea>
          </div>
        )}
      </div>

      {/* Websites Section */}
      <div>
        <button type="button" onChange={(e) => handleChange(e, index)} onClick={addWebsite}>Add Websites</button>
        {showWebsites && (
              <div key={index}>
                <label>Website:</label>
                <input
                  type="url"
                  name={`websites`}
                  pattern="https?://.*"
                  title="Enter a valid URL"
                  onChange={handleChange}
                  value={`formData.websites[${index}]`}
                  required
                />
              </div>
            )}
            <button type="button" onClick={removeWebsite}>Remove All Websites</button>
      </div>
      <div>
        <label>Job Application URL:</label>
        <input type="text" name="url" value={formData.url} onChange={handleChange} required />
      </div>
      <button type="submit">Submit</button>
    </form>
  );
}













// export default function Home() {
  
  
  
//   return (
//     <form
//       method="POST"
//       action={"/user_text"}
//       encType="multipart/form-data"
//     >
//       <Stack direction={'row'} spacing={2}>
//         <TextField
//           label="Message"
//           fullWidth
//           value={message}
//           onChange={(e) => setMessage(e.target.value)}
//           onKeyDown={handleKeyPress}
//           disabled={isLoading}
//           name="user_query"
//         />
//         <Button type="submit" variant="contained" onClick={(e) => sendMessage(e)} disabled={isLoading}>
//           {isLoading ? 'Submitting' : 'Submit'}
//         </Button>
//       </Stack>
//     </form>
//   );
// }
