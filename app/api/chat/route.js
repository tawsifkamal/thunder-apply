import fs from 'fs';
import path from 'path';

// Named export for POST method
export async function POST(req, res) {
  try {
    // Get the form data from the request body
    const formData = await req.json();

    // Define the path to the file
    const filePath = path.join(process.cwd(), 'profile_test.json');

    // Write the form data to the profile.json file
    fs.writeFileSync(filePath, JSON.stringify(formData, null, 2), 'utf8');

    // Send a success response
    return new Response(JSON.stringify({ message: 'Form data saved successfully' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error writing file:', error);
    return new Response(JSON.stringify({ message: 'Failed to save form data' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}









// const { Blob } = require('buffer');

// const handleFileInput = async (req) => {
//     // console.log("From inside route.js, the cwd is " + process.cwd());
//     const data = await req.formData();
//     const resume = data.getAll('resume');
//     const dir = '/documents/';
//     if (!resume) {
//       return NextResponse.json({success: false});
//     }
  
//     // Iterate over the array of files and perform the following:
//     // 1) Convert it to a blob
//     // 2) Feed the blob to a document loader to create Docs
  
//     files.forEach(async (file) => {
//       const bytes = await file.arrayBuffer();
//       const buffer = Buffer.from(bytes);
//       const blob = new Blob([buffer]);
//       let loader;
//       let docs;
//       const fileType = file.name.substring(file.name.lastIndexOf('.'), file.name.length);
//       if (fileType === '.pdf') {
//         loader = new PDFLoader(blob, {splitPages: false});
//         docs = await loader.load();
//       } else if (fileType === '.csv') {
//         loader = new CSVLoader(blob);
//         docs = await loader.load();
//       }  else if (fileType === '.docx') {
//         loader = new DocxLoader(blob);
//         docs = await loader.load();
//       } else if (fileType === '.pptx') {
//         loader = new PPTXLoader(blob);
//         docs = await loader.load();
//       } else { // Potentially unsupported types
//         return NextResponse.json({success: false});
//       }
//     });
//     console.log("Files successfully embedded and vectorized");
//     return NextResponse.json({success: true});
//   }