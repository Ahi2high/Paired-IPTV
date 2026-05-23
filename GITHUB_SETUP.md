# GitHub Setup Commands

Replace `YOUR_USERNAME` with your GitHub username.

```bat
cd AHI-IPTV-Paired-Player-GitHub-Ready
git init
git add .
git commit -m "Initial release: AHI IPTV Paired Player v1.1"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/AHI-IPTV-Paired-Player.git
git push -u origin main
```

## Create a GitHub Release

After pushing:

1. Go to your repository on GitHub.
2. Click **Releases**.
3. Click **Draft a new release**.
4. Tag:

```text
v1.1.0
```

5. Release title:

```text
AHI IPTV Paired Player v1.1 TRUE AUDIO SPLIT
```

6. Upload the ZIP package if desired.
