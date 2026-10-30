(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const mode = window.matchMedia('(display-mode: standalone)');
  const android = /Android/i.test(navigator.userAgent);
  const ios = /iPhone|iPad|iPod/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const samsung = /SamsungBrowser/i.test(navigator.userAgent);
  const mobile = android || ios;
  let deferred = null, installed = false, prompting = false;
  const dialog = $('install-dialog');
  function standalone() { return installed || mode.matches || navigator.standalone === true; }
  function message(text) { $('install-status').textContent = text; }
  function refresh() {
    const done = standalone();
    $('install-banner').hidden = done;
    $('install-button').hidden = done;
    $('windows-download').hidden = mobile;
    $('install-now').textContent = mobile ? '홈 화면에 설치' : '휴대폰·태블릿에 설치';
    $('install-button').textContent = mobile ? '홈 화면에 설치' : '폰·태블릿에 설치';
    $('install-native').hidden = !deferred;
    $('install-qr-block').hidden = mobile;
    $('install-steps').hidden = !mobile;
    $('install-dialog-title').textContent = mobile ? '홈 화면에 설치하기' : '휴대폰·태블릿으로 QR을 찍으세요';
    $('install-help-text').textContent = ios
      ? 'Safari의 공유 버튼 → 홈 화면에 추가 → 추가를 누르세요.'
      : samsung
        ? '삼성 인터넷 메뉴(≡)에서 홈 화면 추가를 선택하세요. 메뉴가 다르면 아래 ‘Chrome으로 열기’를 누르세요.'
        : 'Chrome 메뉴(⋮) → 홈 화면에 추가 → 설치를 누르세요. ‘앱 설치’로 표시될 수도 있어요.';
    $('open-chrome').hidden = !android;
  }
  function help() {
    refresh();
    if (!dialog.open) dialog.showModal();
  }
  async function install() {
    if (standalone()) return;
    // On a computer this button transfers the link to a phone, rather than
    // installing a second PC app. Mobile prompts require a direct user tap.
    if (!mobile || !deferred) { help(); return; }
    if (prompting) return;
    const event = deferred;
    deferred = null; prompting = true;
    try {
      await event.prompt();
      const choice = await event.userChoice;
      if (choice.outcome === 'accepted') {
        if (dialog.open) dialog.close();
        message('설치가 진행됩니다. 완료되면 홈 화면의 ‘프랑스어 단어장’을 누르세요.');
      } else message('원할 때 이 버튼을 눌러 다시 설치할 수 있어요.');
    } catch (error) { help(); }
    finally { prompting = false; refresh(); }
  }
  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault(); deferred = event; refresh();
    message('설치 준비가 됐어요. ‘홈 화면에 설치’를 누르세요.');
  });
  window.addEventListener('appinstalled', () => {
    installed = true; deferred = null;
    if (dialog.open) dialog.close();
    refresh();
  });
  if (mode.addEventListener) mode.addEventListener('change', refresh);
  else mode.addListener(refresh);
  $('install-now').onclick = install;
  $('install-button').onclick = install;
  $('install-native').onclick = install;
  $('install-help').onclick = help;
  $('close-install').onclick = () => dialog.close();
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  $('copy-app-link').onclick = async () => {
    const url = new URL('./?install=1', location.href).href;
    try {
      await navigator.clipboard.writeText(url);
      $('copy-app-link').textContent = '링크를 복사했어요';
    } catch (error) {
      $('app-link-text').hidden = false;
      $('app-link-text').select();
    }
  };
  const publicURL = new URL('./?install=1', location.href);
  $('app-link-text').value = publicURL.href;
  $('open-chrome').href = 'intent://' + publicURL.host + publicURL.pathname + publicURL.search + '#Intent;scheme=https;package=com.android.chrome;S.browser_fallback_url=' + encodeURIComponent(publicURL.href) + ';end';
  if ('serviceWorker' in navigator) {
    const hadController = !!navigator.serviceWorker.controller;
    let reloading = false;
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (hadController && !reloading) { reloading = true; location.reload(); }
    });
    navigator.serviceWorker.ready.then(() => {
      navigator.storage?.persist?.().catch(() => {});
      if (!deferred) message('한 번 설치하면 홈 화면 아이콘으로 바로 열려요.');
    }).catch(() => {});
  }
  refresh();
})();
