(function () {
    'use strict';

    var COLUMN_COUNT = 9;
    var LERP_SPEED = 0.07;
    var MOUSE_LERP = 0.06;
    var MOUSE_FADE_IN = 0.03;
    var SCROLL_THRESHOLD = 30;

    var section = document.querySelector('body.landing section.welcome');
    if (!section) return;

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var headerline = document.querySelector('header .headerline');

    // --- Color palette from CSS custom properties ---

    var currentColors = { sky: null, white: null };
    var targetColors = { sky: null, white: null };

    function parseColor(value) {
        value = value.trim();
        if (value.charAt(0) === '#') {
            var hex = value.substring(1);
            if (hex.length === 3) {
                hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
            }
            if (hex.length === 8) {
                hex = hex.substring(0, 6);
            }
            var num = parseInt(hex, 16);
            return [num >> 16, (num >> 8) & 0xff, num & 0xff];
        }
        var match = value.match(/(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/);
        if (match) {
            return [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])];
        }
        return [0, 0, 0];
    }

    function readColors() {
        var style = getComputedStyle(document.documentElement);
        targetColors.sky = parseColor(style.getPropertyValue('--lake-animated-column-background-gradient-start'));
        targetColors.white = parseColor(style.getPropertyValue('--main-body-background-color'));

        if (!currentColors.sky) {
            currentColors.sky = targetColors.sky.slice();
            currentColors.white = targetColors.white.slice();
        }
    }

    function lerpColor(current, target, t) {
        for (var i = 0; i < 3; i++) {
            current[i] += (target[i] - current[i]) * t;
        }
    }

    function rgb(c) {
        return 'rgb(' + (c[0] | 0) + ',' + (c[1] | 0) + ',' + (c[2] | 0) + ')';
    }

    readColors();

    // --- DOM setup ---

    var container = document.createElement('div');
    container.className = 'wave-bg';

    var cols = [];
    for (var i = 0; i < COLUMN_COUNT; i++) {
        var col = document.createElement('div');
        col.className = 'wave-bg-col';
        container.appendChild(col);
        cols.push(col);
    }

    document.body.insertBefore(container, document.body.firstChild);

    function updateContainerHeight() {
        var rect = section.getBoundingClientRect();
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        container.style.height = (rect.bottom + scrollTop) + 'px';
    }

    updateContainerHeight();
    window.addEventListener('resize', updateContainerHeight);

    section.style.background = 'transparent';

    // --- Header scroll behavior ---

    var headerScrolled = false;

    function updateHeaderScroll() {
        var scrollY = window.pageYOffset || document.documentElement.scrollTop;
        var shouldBeScrolled = scrollY > SCROLL_THRESHOLD;

        if (shouldBeScrolled !== headerScrolled) {
            headerScrolled = shouldBeScrolled;
            if (headerline) {
                if (headerScrolled) {
                    headerline.classList.add('header-scrolled');
                } else {
                    headerline.classList.remove('header-scrolled');
                }
            }
        }
    }

    window.addEventListener('scroll', updateHeaderScroll, { passive: true });
    updateHeaderScroll();

    // --- Animation state ---

    var wave = new Float32Array(COLUMN_COUNT);
    for (var j = 0; j < COLUMN_COUNT; j++) wave[j] = 0.6;

    var mouseXNorm = 0.5;
    var mouseYNorm = 0.5;
    var smoothMouseX = 0.5;
    var smoothMouseY = 0.5;
    var mousePresence = 0;
    var targetMousePresence = 0;

    var isVisible = true;
    var rafId = null;

    // --- Mouse tracking ---

    var isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    if (!isTouch) {
        document.addEventListener('mousemove', function (e) {
            var rect = container.getBoundingClientRect();
            if (e.clientY < rect.top || e.clientY > rect.bottom ||
                e.clientX < rect.left || e.clientX > rect.right) {
                targetMousePresence = 0;
                return;
            }
            mouseXNorm = (e.clientX - rect.left) / rect.width;
            mouseYNorm = (e.clientY - rect.top) / rect.height;
            targetMousePresence = 1;
        });
    }

    // --- IntersectionObserver ---

    var observer = new IntersectionObserver(function (entries) {
        isVisible = entries[0].isIntersecting;
        if (isVisible && !rafId) {
            rafId = requestAnimationFrame(frame);
        }
    }, { threshold: 0 });

    observer.observe(container);

    // --- Dark mode observer ---

    var modeObserver = new MutationObserver(function () {
        readColors();
    });

    modeObserver.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
    });

    // --- Animation loop ---

    function frame(ts) {
        if (!isVisible) {
            rafId = null;
            return;
        }

        var t = ts * 0.0012;

        lerpColor(currentColors.sky, targetColors.sky, 0.04);
        lerpColor(currentColors.white, targetColors.white, 0.04);

        smoothMouseX += (mouseXNorm - smoothMouseX) * MOUSE_LERP;
        smoothMouseY += (mouseYNorm - smoothMouseY) * MOUSE_LERP;
        mousePresence += (targetMousePresence - mousePresence) * MOUSE_FADE_IN;

        var mouseCol = smoothMouseX * (COLUMN_COUNT - 1);

        for (var i = 0; i < COLUMN_COUNT; i++) {
            var idlePeak = 0.55
                + 0.48 * Math.sin(t * 0.9 + i * 0.5)
                + 0.27 * Math.sin(t * 0.5 - i * 0.3)
                + 0.15 * Math.sin(t * 1.5 + i * 0.8);

            var dist = Math.abs(i - mouseCol);
            var mouseWeight = Math.exp(-dist * dist / 2.0) * mousePresence;

            var mouseTargetPeak = 0.10 + smoothMouseY * 0.80;

            var targetPeak = idlePeak * (1 - mouseWeight) + mouseTargetPeak * mouseWeight;

            wave[i] += (targetPeak - wave[i]) * LERP_SPEED;
        }

        // Render gradients
        var skyCol = rgb(currentColors.sky);
        var whiteCol = rgb(currentColors.white);

        for (var k = 0; k < COLUMN_COUNT; k++) {
            var p = wave[k];

            var fadeStart = (10 + p * 45).toFixed(1);
            var fadeEnd = Math.min(100, parseFloat(fadeStart) + 65).toFixed(1);

            // Mouse pushes sky away → white bloom around cursor
            var distToMouse = Math.abs(k - mouseCol);
            var activeWeight = Math.exp(-distToMouse * distToMouse / 2.0) * mousePresence;
            fadeStart = Math.max(0, parseFloat(fadeStart) - activeWeight * 30).toFixed(1);
            fadeEnd = Math.min(100, parseFloat(fadeStart) + 50).toFixed(1);

            cols[k].style.background =
                'linear-gradient(to bottom, ' + skyCol + ' 0%, ' + skyCol + ' ' + fadeStart + '%, ' + whiteCol + ' ' + fadeEnd + '%)';
        }

        rafId = requestAnimationFrame(frame);
    }

    rafId = requestAnimationFrame(frame);
})();
