const CTA_TARGET_URL = '/service/quotation/machine/';

document.addEventListener('DOMContentLoaded', () => {
  const heroVideo = document.getElementById('heroVideo');
  const ctaButton = document.getElementById('ctaButton');

  if (heroVideo instanceof HTMLVideoElement) {
    const syncPlaybackRate = () => {
      heroVideo.playbackRate = 1;
    };

    if (heroVideo.readyState >= 1) {
      syncPlaybackRate();
    } else {
      heroVideo.addEventListener('loadedmetadata', syncPlaybackRate, {
        once: true,
      });
    }
  }

  if (ctaButton) {
    ctaButton.addEventListener('click', () => {
      window.location.href = CTA_TARGET_URL;
    });
  }
});