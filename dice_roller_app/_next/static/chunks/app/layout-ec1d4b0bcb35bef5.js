(self.webpackChunk_N_E = self.webpackChunk_N_E || []).push([
  [185],
  {
    395: function (e, t, n) {
      (Promise.resolve().then(n.bind(n, 7240)),
        Promise.resolve().then(n.t.bind(n, 7800, 23)),
        Promise.resolve().then(n.t.bind(n, 2544, 23)),
        Promise.resolve().then(n.t.bind(n, 3054, 23)),
        Promise.resolve().then(n.bind(n, 2438)));
    },
    6463: function (e, t, n) {
      "use strict";
      var r = n(1169);
      (n.o(r, "useParams") &&
        n.d(t, {
          useParams: function () {
            return r.useParams;
          },
        }),
        n.o(r, "usePathname") &&
          n.d(t, {
            usePathname: function () {
              return r.usePathname;
            },
          }),
        n.o(r, "useSearchParams") &&
          n.d(t, {
            useSearchParams: function () {
              return r.useSearchParams;
            },
          }));
    },
    2438: function (e, t, n) {
      "use strict";
      n.d(t, {
        CSPostHogProvider: function () {
          return c;
        },
      });
      var r = n(7437),
        a = n(2477),
        o = n(2265),
        s = (0, o.createContext)({ client: a.ZP });
      function i(e) {
        var t = e.children,
          n = e.client,
          r = e.apiKey,
          i = e.options,
          c = (0, o.useMemo)(
            function () {
              return (n &&
                r &&
                console.warn(
                  "[PostHog.js] You have provided both a client and an apiKey to PostHogProvider. The apiKey will be ignored in favour of the client.",
                ),
              n &&
                i &&
                console.warn(
                  "[PostHog.js] You have provided both a client and options to PostHogProvider. The options will be ignored in favour of the client.",
                ),
              n)
                ? n
                : (r &&
                    (a.ZP.__loaded &&
                      console.warn(
                        "[PostHog.js] was already loaded elsewhere. This may cause issues.",
                      ),
                    a.ZP.init(r, i)),
                  a.ZP);
            },
            [n, r],
          );
        return o.createElement(s.Provider, { value: { client: c } }, t);
      }
      function c(e) {
        let { children: t } = e;
        return (0, r.jsx)(i, { client: a.ZP, children: t });
      }
      a.ZP.init("phc_Jj8yleUItTiMitqy3CUx5gdXelikRJYrvlaJJehCnq3", {
        api_host: "https://t.rollmydice.app",
        person_profiles: "identified_only",
      });
    },
    3054: function () {},
    2544: function (e) {
      e.exports = {
        style: {
          fontFamily: "'__geistMono_c3aa02', '__geistMono_Fallback_c3aa02'",
        },
        className: "__className_c3aa02",
        variable: "__variable_c3aa02",
      };
    },
    7800: function (e) {
      e.exports = {
        style: {
          fontFamily: "'__geistSans_1e4310', '__geistSans_Fallback_1e4310'",
        },
        className: "__className_1e4310",
        variable: "__variable_1e4310",
      };
    },
    7240: function (e, t, n) {
      "use strict";
      n.d(t, {
        SpeedInsights: function () {
          return h;
        },
      });
      var r = n(2265),
        a = n(6463),
        o = () => {
          window.si ||
            (window.si = function () {
              for (var e = arguments.length, t = Array(e), n = 0; n < e; n++)
                t[n] = arguments[n];
              (window.siq = window.siq || []).push(t);
            });
        };
      function s() {
        return false;
      }
      function i(e) {
        return new RegExp(
          "/".concat(e.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "(?=[/?#]|$)"),
        );
      }
      var c = "https://va.vercel-scripts.com/v1/speed-insights",
        l = "".concat(c, "/script.js"),
        u = "".concat(c, "/script.debug.js");
      function d(e) {
        let t = (0, r.useRef)(null);
        return (
          (0, r.useEffect)(() => {
            if (t.current) e.route && t.current(e.route);
            else {
              let n = (function () {
                var e;
                let t =
                  arguments.length > 0 && void 0 !== arguments[0]
                    ? arguments[0]
                    : {};
                if (!("undefined" != typeof window) || null === t.route)
                  return null;
                o();
                let n = !!t.dsn,
                  r =
                    t.scriptSrc ||
                    (n ? l : "/_vercel/speed-insights/script.js");
                if (
                  document.head.querySelector('script[src*="'.concat(r, '"]'))
                )
                  return null;
                t.beforeSend &&
                  (null == (e = window.si) ||
                    e.call(window, "beforeSend", t.beforeSend));
                let a = document.createElement("script");
                return (
                  (a.src = r),
                  (a.defer = !0),
                  (a.dataset.sdkn =
                    "@vercel/speed-insights" +
                    (t.framework ? "/".concat(t.framework) : "")),
                  (a.dataset.sdkv = "1.0.12"),
                  t.sampleRate &&
                    (a.dataset.sampleRate = t.sampleRate.toString()),
                  t.route && (a.dataset.route = t.route),
                  t.endpoint && (a.dataset.endpoint = t.endpoint),
                  t.dsn && (a.dataset.dsn = t.dsn),
                  (a.onerror = () => {
                    console.log(
                      "[Vercel Speed Insights] Failed to load script from ".concat(
                        r,
                        ". Please check if any content blockers are enabled and try again.",
                      ),
                    );
                  }),
                  document.head.appendChild(a),
                  {
                    setRoute: (e) => {
                      a.dataset.route = null != e ? e : void 0;
                    },
                  }
                );
              })({ framework: e.framework || "react", ...e });
              n && (t.current = n.setRoute);
            }
          }, [e.route]),
          null
        );
      }
      var f = () => {
        let e = (0, a.useParams)(),
          t = (0, a.useSearchParams)() || new URLSearchParams(),
          n = (0, a.usePathname)(),
          r = { ...Object.fromEntries(t.entries()), ...(e || {}) };
        return e
          ? (function (e, t) {
              if (!e || !t) return e;
              let n = e;
              try {
                let e = Object.entries(t);
                for (let [t, r] of e)
                  if (!Array.isArray(r)) {
                    let e = i(r);
                    e.test(n) && (n = n.replace(e, "/[".concat(t, "]")));
                  }
                for (let [t, r] of e)
                  if (Array.isArray(r)) {
                    let e = i(r.join("/"));
                    e.test(n) && (n = n.replace(e, "/[...".concat(t, "]")));
                  }
                return n;
              } catch (t) {
                return e;
              }
            })(n, r)
          : null;
      };
      function p(e) {
        let t = f();
        return r.createElement(d, { route: t, ...e, framework: "next" });
      }
      function h(e) {
        return r.createElement(
          r.Suspense,
          { fallback: null },
          r.createElement(p, { ...e }),
        );
      }
    },
  },
  function (e) {
    (e.O(0, [571, 878, 971, 23, 560], function () {
      return e((e.s = 395));
    }),
      (_N_E = e.O()));
  },
]);
