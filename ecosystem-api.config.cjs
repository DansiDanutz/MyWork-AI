module.exports = {
  apps: [
    {
      name: 'mywork-api',
      script: '/home/Memo1981/MyWork-AI/tools/api_server.py',
      interpreter: 'python3',
      cwd: '/home/Memo1981/MyWork-AI',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      restart_delay: 3000,
      max_restarts: 10,
      min_uptime: '10s',
      out_file: '/home/Memo1981/.pm2/logs/mywork-api-out.log',
      error_file: '/home/Memo1981/.pm2/logs/mywork-api-err.log',
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      args: ['--host', '0.0.0.0', '--port', '8420'],
    },
  ],
};
