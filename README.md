# Iranian Road Information Telegram Bot

This project provides real-time road condition updates for Iranian roads via a Telegram bot. It consists of two main components:
1. A **web scraper** that fetches road condition data from a public source.
2. A **Telegram bot** that delivers the scraped data to users.

---

## Features
- **Real-time updates**: Fetches the latest road conditions every 5 minutes.
- **Interactive menus**: Users can navigate through different road conditions and closures.
- **Persistent data**: Stores scraped data in a `data.json` file for easy access.

---

## Prerequisites

Before running this project, ensure you have the following:

1. **Python 3.8 or higher**: Download and install Python from [python.org](https://www.python.org/).
2. **A Telegram bot token**:
   - Create a bot using [BotFather](https://core.telegram.org/bots#botfather).
   - Save the token provided by BotFather. You’ll need it to run the bot.
3. **Google Chrome**: The scraper uses Selenium with ChromeDriver. Make sure Chrome is installed on your system.
4. **ChromeDriver**: Download the version of ChromeDriver that matches your Chrome version from [here](https://sites.google.com/chromium.org/driver/).

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Iranian-Road-Info-Bot.git
   cd Iranian-Road-Info-Bot