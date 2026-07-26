# Machine state — measured on `lenovo`

_Captured 2026-07-26T15:09:04+02:00 by `setup/bootstrap-remote-access.sh`._
_Measured, not remembered. Re-run the script to refresh._

## Privilege

```
sudo -n true => passwordless sudo IS available
/etc/sudoers.d:
  total 12
  -r--r----- 1 root root  600 Jul 22 22:08 50-workbench-agent
  -r--r----- 1 root root   36 Jul 22 21:30 90-agent-nopasswd
  -r--r----- 1 root root 1068 Jan 29  2024 README
```

## ~/bin

```
  total 28
  drwxrwxr-x 2 lukashoerup lukashoerup 4096 Jul 22 21:56 __pycache__
  -rwxrwxr-x 1 lukashoerup lukashoerup 3110 Jul 22 21:23 github-device-login.py
  -rwxrwxr-x 1 lukashoerup lukashoerup 5950 Jul 22 21:45 new-project.sh
  lrwxrwxrwx 1 lukashoerup lukashoerup   41 Jul 22 21:46 notify.py -> /home/lukashoerup/workbench/bin/notify.py
  -rwxrwxr-x 1 lukashoerup lukashoerup 6554 Jul 22 21:52 ollama-benchmark.py
  lrwxrwxrwx 1 lukashoerup lukashoerup   49 Jul 22 22:12 publish-status.sh -> /home/lukashoerup/workbench/bin/publish-status.sh
  -rwxrwxr-x 1 lukashoerup lukashoerup 2761 Jul 22 21:07 telegram-capture-chatid.py
  lrwxrwxrwx 1 lukashoerup lukashoerup   49 Jul 22 21:46 telegram-setup.py -> /home/lukashoerup/workbench/bin/telegram-setup.py
  lrwxrwxrwx 1 lukashoerup lukashoerup   49 Jul 22 21:46 watchdog-check.sh -> /home/lukashoerup/workbench/bin/watchdog-check.sh
  lrwxrwxrwx 1 lukashoerup lukashoerup   36 Jul 22 21:46 work -> /home/lukashoerup/workbench/bin/work
  lrwxrwxrwx 1 lukashoerup lukashoerup   51 Jul 22 22:12 workbench-status.py -> /home/lukashoerup/workbench/bin/workbench-status.py
```

## Toolchain

```
claude: NOT INSTALLED
uv: NOT INSTALLED
python3: /usr/bin/python3
ollama: /usr/local/bin/ollama
git: /usr/bin/git
systemctl: /usr/bin/systemctl
tailscale: /usr/bin/tailscale
```

## Timers

```
  NEXT                             LEFT LAST                            PASSED UNIT                           ACTIVATES
  Sun 2026-07-26 15:13:31 CEST 4min 26s Sun 2026-07-26 14:58:14 CEST 10min ago workbench-watchdog.timer       workbench-watchdog.service
  Sun 2026-07-26 15:29:32 CEST    20min Sun 2026-07-26 14:59:14 CEST  9min ago workbench-status.timer         workbench-status.service
  Sun 2026-07-26 19:46:14 CEST 4h 37min Sat 2026-07-25 19:46:14 CEST   19h ago launchpadlib-cache-clean.timer launchpadlib-cache-clean.service
  
  3 timers listed.
```
