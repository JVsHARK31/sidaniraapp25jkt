import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

// Function to create necessary Vercel configuration files
function setupVercelDeployment() {
  console.log("Setting up Vercel deployment for Sidanira Flask application...");
  
  // Create vercel.json configuration file
  const vercelConfig = {
    "version": 2,
    "builds": [
      {
        "src": "src/main.py",
        "use": "@vercel/python"
      }
    ],
    "routes": [
      {
        "src": "/(.*)",
        "dest": "src/main.py"
      }
    ]
  };
  
  fs.writeFileSync('vercel.json', JSON.stringify(vercelConfig, null, 2));
  console.log("✅ Created vercel.json configuration file");
  
  // Create requirements.txt if it doesn't exist or update it
  try {
    const requirements = fs.readFileSync('requirements.txt', 'utf8');
    console.log("✅ Found existing requirements.txt file");
    
    // Check if it has the necessary packages
    const requiredPackages = ['flask', 'gunicorn'];
    let needsUpdate = false;
    
    for (const pkg of requiredPackages) {
      if (!requirements.includes(pkg)) {
        needsUpdate = true;
        console.log(`Adding missing dependency: ${pkg}`);
      }
    }
    
    if (needsUpdate) {
      const updatedRequirements = requirements + '\n' + 
        requiredPackages.filter(pkg => !requirements.includes(pkg)).join('\n');
      fs.writeFileSync('requirements.txt', updatedRequirements);
      console.log("✅ Updated requirements.txt with necessary dependencies");
    }
  } catch (error) {
    // Create a new requirements.txt file
    const basicRequirements = 
      "flask\n" +
      "gunicorn\n" +
      "sqlalchemy\n";
    
    fs.writeFileSync('requirements.txt', basicRequirements);
    console.log("✅ Created new requirements.txt file with basic dependencies");
  }
  
  // Create .vercelignore file
  const vercelIgnore = 
    ".git\n" +
    "__pycache__\n" +
    "*.pyc\n" +
    "env/\n" +
    "venv/\n";
  
  fs.writeFileSync('.vercelignore', vercelIgnore);
  console.log("✅ Created .vercelignore file");
  
  // Instructions for deployment
  console.log("\n🚀 Your Flask application is now ready for Vercel deployment!");
  console.log("\nTo deploy, follow these steps:");
  console.log("1. Install Vercel CLI: npm install -g vercel");
  console.log("2. Run 'vercel login' to authenticate");
  console.log("3. Run 'vercel' in the project directory to deploy");
  console.log("\nAlternatively, you can use the Vercel dashboard:");
  console.log("1. Push your code to a Git repository (GitHub, GitLab, etc.)");
  console.log("2. Import the repository in the Vercel dashboard");
  console.log("3. Vercel will automatically detect your Flask application and deploy it");
  
  console.log("\n⚠️ Important notes:");
  console.log("- Vercel uses serverless functions, so your application needs to be stateless");
  console.log("- SQLite database won't persist between deployments; consider using a managed database service");
  console.log("- You may need to adjust your application to work with serverless architecture");
}

// Run the setup
setupVercelDeployment(); 