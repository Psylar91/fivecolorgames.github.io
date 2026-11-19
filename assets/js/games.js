// 게임 목록 페이지(/games/). SNS 프로필 링크가 가리키는 곳이다.
// - 목록은 /games/games.json에서 읽는다. 새 게임은 그 파일에 한 줄을 더하고 아이콘(assets/img/games/<id>.webp)을 만들면 나온다.
// - 주소의 ?from=<플랫폼>을 Google Play 주소의 referrer(utm_source)로 넘긴다. 없거나 형식이 틀리면 website.
// - 언어: ?lang=ko|en, 없으면 브라우저 언어(ko면 한국어, 아니면 영어).
(function () {
  "use strict";

  var params = new URLSearchParams(location.search);
  var rawFrom = (params.get("from") || "").trim().toLowerCase();
  var source = /^[a-z0-9_-]{1,32}$/.test(rawFrom) ? rawFrom : "website";

  var langParam = params.get("lang");
  var browserLang = (navigator.languages && navigator.languages[0]) || navigator.language || "";
  var lang = langParam === "ko" || langParam === "en" ? langParam : (/^ko\b/i.test(browserLang) ? "ko" : "en");

  var TEXT = {
    ko: {
      title: "FiveColorGames 게임",
      heading: "게임 목록",
      lead: "FiveColorGames의 모바일 퍼즐 게임을 Google Play에서 받아 보세요.",
      button: "Google Play에서 받기",
      buttonLabel: function (name) { return name + " Google Play에서 받기"; },
      iconAlt: function (name) { return name + " 아이콘"; },
      other: "English",
      otherLang: "en",
      home: "홈페이지",
      homeHref: "/",
      error: "목록을 불러오지 못했습니다. 홈페이지에서 게임을 볼 수 있습니다."
    },
    en: {
      title: "FiveColorGames Games",
      heading: "Our games",
      lead: "Get FiveColorGames mobile puzzle games on Google Play.",
      button: "Get it on Google Play",
      buttonLabel: function (name) { return "Get " + name + " on Google Play"; },
      iconAlt: function (name) { return name + " icon"; },
      other: "한국어",
      otherLang: "ko",
      home: "Website",
      homeHref: "/en/",
      error: "We couldn't load the list. You can find our games on our website."
    }
  };
  var t = TEXT[lang];

  function playUrl(pkg) {
    var referrer = "utm_source=" + source + "&utm_medium=profile&utm_campaign=sns_profile";
    return "https://play.google.com/store/apps/details?id=" + encodeURIComponent(pkg) +
      "&referrer=" + encodeURIComponent(referrer);
  }

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text) node.textContent = text;
    return node;
  }

  function setText(id, value) {
    var node = document.getElementById(id);
    if (node) node.textContent = value;
  }

  // 페이지 글자와 언어 전환 링크
  document.documentElement.lang = lang;
  document.title = t.title;
  setText("list-heading", t.heading);
  setText("list-lead", t.lead);
  var toggle = document.getElementById("lang-toggle");
  if (toggle) {
    var next = new URLSearchParams(location.search);
    next.set("lang", t.otherLang);
    toggle.href = "?" + next.toString();
    toggle.textContent = t.other;
    toggle.lang = t.otherLang;
    toggle.hreflang = t.otherLang;
  }
  var home = document.getElementById("home-link");
  if (home) { home.href = t.homeHref; home.textContent = t.home; }
  var brand = document.getElementById("home-brand");
  if (brand) brand.href = t.homeHref;

  var list = document.getElementById("game-list");

  function render(games) {
    list.textContent = "";
    games.forEach(function (g) {
      var name = g.name[lang] || g.name.en;
      var otherName = g.name[t.otherLang];
      var li = el("li", "game-row");

      var icon = el("img", "game-row-icon");
      icon.src = "/assets/img/games/" + g.id + ".webp";
      icon.width = 72;
      icon.height = 72;
      icon.alt = t.iconAlt(name);
      li.appendChild(icon);

      var body = el("div", "game-row-body");
      body.appendChild(el("h2", null, name));
      if (otherName && otherName !== name) {
        var alt = el("p", "game-row-alt", otherName);
        alt.lang = t.otherLang;
        body.appendChild(alt);
      }
      body.appendChild(el("p", "game-row-tagline", g.tagline[lang] || g.tagline.en));

      var btn = el("a", "btn btn-primary btn-small game-row-play", t.button);
      btn.href = playUrl(g.package);
      btn.setAttribute("aria-label", t.buttonLabel(name));
      body.appendChild(btn);

      li.appendChild(body);
      list.appendChild(li);
    });
    list.setAttribute("aria-busy", "false");
  }

  function fail() {
    list.setAttribute("aria-busy", "false");
    var msg = el("p", "game-list-error", t.error + " ");
    var link = el("a", null, t.home);
    link.href = t.homeHref + "#games";
    msg.appendChild(link);
    list.replaceWith(msg);
  }

  fetch("/games/games.json", { cache: "no-cache" })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(render)
    .catch(fail);
})();
