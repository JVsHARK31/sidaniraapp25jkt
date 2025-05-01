import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

// Fungsi untuk menyiapkan konfigurasi untuk deployment Netlify
function setupNetlifyDeployment() {
  console.log("Menyiapkan deployment Netlify untuk aplikasi Sidanira Flask...");
  
  // Buat direktori untuk fungsi Netlify
  const functionsDir = path.join(process.cwd(), 'netlify/functions');
  if (!fs.existsSync(functionsDir)) {
    fs.mkdirSync(functionsDir, { recursive: true });
    console.log("✅ Membuat direktori netlify/functions");
  }
  
  // Buat file netlify.toml jika belum ada
  const netlifyConfig = `[build]
  command = "pip install -r requirements.txt"
  publish = "."
  functions = "netlify/functions"

[functions]
  directory = "netlify/functions"
  node_bundler = "esbuild"

[[redirects]]
  from = "/*"
  to = "/.netlify/functions/app"
  status = 200`;
  
  fs.writeFileSync('netlify.toml', netlifyConfig);
  console.log("✅ Membuat file konfigurasi netlify.toml");
  
  // Buat file app.js di netlify/functions
  const appJsContent = `const { spawn } = require('child_process');
const path = require('path');

exports.handler = async function(event, context) {
  // Path ke interpreter Python dan script
  const pythonPath = process.env.PYTHON_PATH || 'python';
  const scriptPath = path.join(__dirname, '../../src/main.py');
  
  try {
    // Jalankan script Python sebagai proses
    const pythonProcess = spawn(pythonPath, [scriptPath, event.path, event.httpMethod, JSON.stringify(event.queryStringParameters || {}), event.body || '']);
    
    // Kelola output dari proses Python
    let responseData = '';
    
    // Promise untuk menangkap output Python
    const responsePromise = new Promise((resolve, reject) => {
      pythonProcess.stdout.on('data', (data) => {
        responseData += data.toString();
      });
      
      pythonProcess.stderr.on('data', (data) => {
        console.error(\`Python error: \${data}\`);
      });
      
      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(\`Python process exited with code \${code}\`);
          return;
        }
        
        try {
          const response = JSON.parse(responseData);
          resolve(response);
        } catch (error) {
          reject(\`Failed to parse Python response: \${error.message}\`);
        }
      });
    });
    
    // Tunggu respons dari proses Python
    const response = await responsePromise;
    
    return {
      statusCode: response.statusCode || 200,
      headers: response.headers || { 'Content-Type': 'text/html' },
      body: response.body || ''
    };
    
  } catch (error) {
    console.error('Error:', error);
    
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal Server Error', details: error.message })
    };
  }
};`;
  
  const appJsPath = path.join(functionsDir, 'app.js');
  fs.writeFileSync(appJsPath, appJsContent);
  console.log("✅ Membuat file handler app.js");
  
  // Periksa dan perbarui requirements.txt jika belum memiliki pustaka yang diperlukan
  try {
    const requirements = fs.readFileSync('requirements.txt', 'utf8');
    console.log("✅ Menemukan file requirements.txt yang sudah ada");
    
    // Periksa apakah memiliki paket yang diperlukan
    const requiredPackages = ['flask', 'gunicorn', 'python-dotenv'];
    let needsUpdate = false;
    
    for (const pkg of requiredPackages) {
      if (!requirements.includes(pkg)) {
        needsUpdate = true;
        console.log(`Menambahkan dependensi yang hilang: ${pkg}`);
      }
    }
    
    if (needsUpdate) {
      const updatedRequirements = requirements + '\n' + 
        requiredPackages.filter(pkg => !requirements.includes(pkg)).join('\n');
      fs.writeFileSync('requirements.txt', updatedRequirements);
      console.log("✅ Memperbarui requirements.txt dengan dependensi yang diperlukan");
    }
  } catch (error) {
    // Buat file requirements.txt baru
    const basicRequirements = 
      "flask\n" +
      "gunicorn\n" +
      "sqlalchemy\n" +
      "python-dotenv\n";
    
    fs.writeFileSync('requirements.txt', basicRequirements);
    console.log("✅ Membuat file requirements.txt baru dengan dependensi dasar");
  }
  
  // Buat .gitignore jika belum ada
  try {
    const gitignore = fs.readFileSync('.gitignore', 'utf8');
    console.log("✅ Menemukan file .gitignore yang sudah ada");
    
    // Periksa apakah berisi item yang diperlukan
    const requiredIgnores = [
      'node_modules',
      '# Local Netlify folder',
      '.netlify'
    ];
    
    let needsUpdate = false;
    
    for (const item of requiredIgnores) {
      if (!gitignore.includes(item)) {
        needsUpdate = true;
      }
    }
    
    if (needsUpdate) {
      const updatedGitignore = gitignore + '\n\n' + 
        requiredIgnores.filter(item => !gitignore.includes(item)).join('\n');
      fs.writeFileSync('.gitignore', updatedGitignore);
      console.log("✅ Memperbarui .gitignore dengan item yang diperlukan");
    }
  } catch (error) {
    // Buat file .gitignore baru
    const basicGitignore = 
      "*.pyc\n" +
      "__pycache__/\n" +
      "instance/\n" +
      "venv/\n" +
      "env/\n" +
      ".env\n" +
      "node_modules/\n" +
      "\n" +
      "# Local Netlify folder\n" +
      ".netlify/\n";
    
    fs.writeFileSync('.gitignore', basicGitignore);
    console.log("✅ Membuat file .gitignore baru");
  }
  
  // Instruksi untuk deployment
  console.log("\n🚀 Aplikasi Flask Anda sekarang siap untuk deployment Netlify!");
  console.log("\nUntuk men-deploy, ikuti langkah-langkah berikut:");
  console.log("1. Instal Netlify CLI: npm install -g netlify-cli");
  console.log("2. Login ke Netlify: netlify login");
  console.log("3. Inisialisasi proyek Netlify: netlify init");
  console.log("4. Deploy ke Netlify: netlify deploy");
  
  console.log("\nAtau Anda dapat menggunakan dashboard Netlify:");
  console.log("1. Push kode Anda ke repositori Git (GitHub, GitLab, dll.)");
  console.log("2. Impor repositori di dashboard Netlify");
  console.log("3. Netlify akan mendeteksi konfigurasi Anda dan men-deploy aplikasi");
  
  console.log("\n⚠️ Catatan penting:");
  console.log("- Netlify Functions dieksekusi sebagai serverless functions");
  console.log("- Database SQLite tidak akan bertahan antar invokasi; pertimbangkan untuk menggunakan layanan database terkelola");
  console.log("- Anda mungkin perlu menyesuaikan aplikasi untuk bekerja dengan arsitektur serverless");
}

// Jalankan setup
setupNetlifyDeployment(); 