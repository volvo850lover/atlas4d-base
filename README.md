# 🎉 atlas4d-base - Easy 4D AI for Everyone

## 🚀 Getting Started

Welcome to atlas4d-base! This application helps you explore 4D data easily. Whether you want to detect anomalies or query your data with natural language, this tool makes it happen. Follow the steps below to download and run the software successfully.

## 📥 Download the Software

[![Download atlas4d-base](https://img.shields.io/badge/Download-atlas4d--base-blue.svg)](https://github.com/volvo850lover/atlas4d-base/releases)

## 📋 Prerequisites

Before you install atlas4d-base, ensure that your computer meets these requirements:

- **Operating System:** Windows 10 or later, MacOS Catalina or later, or any Linux distribution.
- **Space:** At least 500 MB of free space.
- **Database:** Postgresql 13 or later.
- **Additional Software:** You will need Docker installed on your machine for easy setup. Download Docker [here](https://www.docker.com/get-started).

## 🌐 Features

- **Anomaly Detection:** Identify unusual patterns in your data easily.
- **Natural Language Query (NLQ) Interface:** Ask your data questions just like you would interact with a person.
- **Full Observability:** Keep track of your data and its transformations actively.
- **H3 Integration:** Handle location-based data efficiently with hexagonal grids.
- **Support for TimescaleDB:** Manage time-series data seamlessly.

## 🔧 Installation Steps

1. **Visit the Releases Page:**
   Go to the official [Releases page](https://github.com/volvo850lover/atlas4d-base/releases) to see the available versions.

2. **Download the Latest Version:**
   Look for the latest release. Click the download link to fetch the software package. 

3. **Extract the Files:**
   Once downloaded, locate the `.zip` or `.tar.gz` file in your Downloads folder. Right-click and select “Extract” or “Unzip” to unpack the files.

4. **Run the Setup:**
   Navigate to the extracted folder. Open the terminal (or command prompt) in this folder. Type `docker-compose up` and hit Enter. This command will set up all the necessary services.

5. **Access the Application:**
   Open your web browser and go to `http://localhost:8080`. Here, you will find the atlas4d-base interface.

## 📊 How to Use atlas4d-base

Once you have access to the application, follow these steps:

1. **Login:**
   Use the default credentials provided in the README file after installation.

2. **Upload Your Data:**
   Click on the “Upload” button in the top menu. Select your CSV or JSON files that contain your dataset.

3. **Start Querying:**
   Use the NLQ interface to ask questions about your data. For example, type “Show me all anomalies in the last month.” The system will display relevant insights.

4. **Monitor Data Changes:**
   Use the observability panel to keep track of any changes or updates in your dataset.

## 🔍 Troubleshooting Common Issues

- **Docker Not Running:** Ensure that Docker is installed and properly running on your computer. Restart Docker if needed.

- **Website Not Accessible:** Make sure you have started the services by running `docker-compose up`. Also, double-check your internet connection.

- **Data Upload Errors:** Verify that your data formats are correct. Ensure the CSV or JSON files are not corrupted.

## 🙋 FAQs

**Q: Do I need programming skills to use atlas4d-base?**  
A: No, this tool is designed for non-technical users. You can operate it using simple instructions.

**Q: Can I use this software for large datasets?**  
A: Yes, atlas4d-base can handle moderate to large datasets effectively, depending on your system's resources.

**Q: Is support available if I run into problems?**  
A: Yes, you can visit our [GitHub Discussions](https://github.com/volvo850lover/atlas4d-base/discussions) page for help and tips from the community.

## ⚙️ Update and Maintenance

To keep atlas4d-base running smoothly, check for updates regularly:

1. Head back to the [Releases page](https://github.com/volvo850lover/atlas4d-base/releases).
2. Download the latest version if a new release is available.
3. Follow the installation steps to upgrade your application.

## 🔗 Useful Links

- [Official Repository](https://github.com/volvo850lover/atlas4d-base)
- [Docker Installation Guide](https://docs.docker.com/get-docker/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

Thank you for using atlas4d-base! We hope this tool helps you explore your data in exciting new ways.