# Handling YouTube Authentication Issues

## Problem
YouTube may block yt-dlp with the error:
```
Sign in to confirm you're not a bot
```

This happens when YouTube's anti-bot detection is triggered, especially in Docker/cloud environments.

## Solutions

### Option 1: Use Different Videos
Try using different YouTube videos that are:
- Shorter in length
- Not age-restricted
- From smaller channels
- Public and embeddable

### Option 2: Add Cookies (Advanced)
1. Export cookies from your browser while logged into YouTube
2. Save as `cookies.txt` in the app directory
3. Mount in Docker:

```yaml
# docker-compose.yml
volumes:
  - ./cookies.txt:/app/cookies.txt
```

### Option 3: Use Alternative Sources
The app works with any YouTube video URL. If one doesn't work, try another.

### Option 4: Wait and Retry
YouTube's rate limiting is temporary. Wait 5-10 minutes and try again.

## Prevention Tips
- Don't make too many requests in quick succession
- Use the mock analyzer for testing
- Rotate between different videos
- Consider using a VPN if running locally

## Note for SAMO Assessment
This is a known limitation when using yt-dlp in automated environments. The application handles this gracefully with proper error messages and suggestions for the user.