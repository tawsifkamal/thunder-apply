"use client"
import { useState } from "react";
import { Box, Stack, TextField, Button } from "@mui/material";

const FileUploader = () => {
    
	const [resume, setResume] = useState([]);

	const handleFileChange = (e) => {
    const temp_resume = e.target.files?.[0];
    if (temp_resume) {
      const fileType = temp_resume.name.substring(temp_resume.name.lastIndexOf('.'), temp_resume.name.length);
      console.log(fileType);
      if (!fileType.match(/(.pdf|.docx)$/)) {
        alert(`${temp_resume.name} is not a supported file type. Must be .pdf or .docx`);
        return;
      }
      setResume([e.target.files?.[0]]);
    }
		// console.log(`New files are: ${files}`);
    // console.log(`Lenght of files is ${files.length}`);
	};
		
	const sendFile = async (e) => {
		e.preventDefault();
		const formData = new FormData();
    formData.append('resume', resume)
		// for (let i = 0; i < file.length; i++) {
		// 	formData.append('file', files[i]);
		// }
		try {
      console.log("From inside FileUploader.js, the cwd is " + process.cwd());
			const response = await fetch('/api/chat', {
				method: 'POST',
        body: formData,
			});
			if (!response.ok) {
        throw new Error(await response.text());
      } else {
        alert("Resume uploaded successfully");
      }
		} catch (error) {
			console.error('Error uploading resume:', error);
		}
	};
	return (
		<form
			method="POST"
			action={"/file_uploads"}
			encType="multipart/form-data" 
		>
			<Stack
        justifyContent={"center"}
        alignItems={"center"}
        direction={"row"}
        gap={5}
				>
        <Button
          component="label"
          role={undefined}
          variant="contained"
          tabIndex={-1}
          //startIcon={<CloudUploadIcon />}
					>
          Upload resume
          <input name="upload_input" type="file" hidden onChange={(e) => handleFileChange(e)} />
        </Button>
        {files.length !== 0 ?
          <Button
					component="label"
					role={undefined}
					variant="contained"
					tabIndex={-1}
					type="submit"
					onClick={(e) => sendFile(e)}
          >
            Send Resume
          </Button> : ""
        }
      </Stack>
		</form>
	);
}

export default FileUploader;