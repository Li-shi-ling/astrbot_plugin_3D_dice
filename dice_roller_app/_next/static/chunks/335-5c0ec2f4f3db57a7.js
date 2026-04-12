(self.webpackChunk_N_E = self.webpackChunk_N_E || []).push([
  [335],
  {
    6335: function (e, t, r) {
      (Promise.resolve().then(r.bind(r, 3879)),
        Promise.resolve().then(r.bind(r, 6168)),
        Promise.resolve().then(r.bind(r, 5550)));
    },
    8030: function (e, t, r) {
      "use strict";
      r.d(t, {
        Z: function () {
          return i;
        },
      });
      var l = r(2265);
      let s = (e) => e.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase(),
        n = function () {
          for (var e = arguments.length, t = Array(e), r = 0; r < e; r++)
            t[r] = arguments[r];
          return t.filter((e, t, r) => !!e && r.indexOf(e) === t).join(" ");
        };
      var o = {
        xmlns: "http://www.w3.org/2000/svg",
        width: 24,
        height: 24,
        viewBox: "0 0 24 24",
        fill: "none",
        stroke: "currentColor",
        strokeWidth: 2,
        strokeLinecap: "round",
        strokeLinejoin: "round",
      };
      let a = (0, l.forwardRef)((e, t) => {
          let {
            color: r = "currentColor",
            size: s = 24,
            strokeWidth: a = 2,
            absoluteStrokeWidth: i,
            className: d = "",
            children: c,
            iconNode: u,
            ...x
          } = e;
          return (0, l.createElement)(
            "svg",
            {
              ref: t,
              ...o,
              width: s,
              height: s,
              stroke: r,
              strokeWidth: i ? (24 * Number(a)) / Number(s) : a,
              className: n("lucide", d),
              ...x,
            },
            [
              ...u.map((e) => {
                let [t, r] = e;
                return (0, l.createElement)(t, r);
              }),
              ...(Array.isArray(c) ? c : [c]),
            ],
          );
        }),
        i = (e, t) => {
          let r = (0, l.forwardRef)((r, o) => {
            let { className: i, ...d } = r;
            return (0, l.createElement)(a, {
              ref: o,
              iconNode: t,
              className: n("lucide-".concat(s(e)), i),
              ...d,
            });
          });
          return ((r.displayName = "".concat(e)), r);
        };
    },
    4392: function (e, t, r) {
      "use strict";
      r.d(t, {
        Z: function () {
          return l;
        },
      });
      let l = (0, r(8030).Z)("ChevronUp", [
        ["path", { d: "m18 15-6-6-6 6", key: "153udz" }],
      ]);
    },
    690: function (e, t, r) {
      "use strict";
      r.d(t, {
        Z: function () {
          return l;
        },
      });
      let l = (0, r(8030).Z)("Info", [
        ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
        ["path", { d: "M12 16v-4", key: "1dtifu" }],
        ["path", { d: "M12 8h.01", key: "e9boi3" }],
      ]);
    },
    7818: function (e, t, r) {
      "use strict";
      r.d(t, {
        default: function () {
          return s.a;
        },
      });
      var l = r(551),
        s = r.n(l);
    },
    551: function (e, t, r) {
      "use strict";
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "default", {
          enumerable: !0,
          get: function () {
            return n;
          },
        }));
      let l = r(9920);
      (r(7437), r(2265));
      let s = l._(r(148));
      function n(e, t) {
        var r;
        let l = {
          loading: (e) => {
            let { error: t, isLoading: r, pastDelay: l } = e;
            return null;
          },
        };
        "function" == typeof e && (l.loader = e);
        let n = { ...l, ...t };
        return (0, s.default)({
          ...n,
          modules: null == (r = n.loadableGenerated) ? void 0 : r.modules,
        });
      }
      ("function" == typeof t.default ||
        ("object" == typeof t.default && null !== t.default)) &&
        void 0 === t.default.__esModule &&
        (Object.defineProperty(t.default, "__esModule", { value: !0 }),
        Object.assign(t.default, t),
        (e.exports = t.default));
    },
    912: function (e, t, r) {
      "use strict";
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "BailoutToCSR", {
          enumerable: !0,
          get: function () {
            return s;
          },
        }));
      let l = r(5592);
      function s(e) {
        let { reason: t, children: r } = e;
        if ("undefined" == typeof window) throw new l.BailoutToCSRError(t);
        return r;
      }
    },
    148: function (e, t, r) {
      "use strict";
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "default", {
          enumerable: !0,
          get: function () {
            return d;
          },
        }));
      let l = r(7437),
        s = r(2265),
        n = r(912),
        o = r(1481);
      function a(e) {
        return { default: e && "default" in e ? e.default : e };
      }
      let i = {
          loader: () => Promise.resolve(a(() => null)),
          loading: null,
          ssr: !0,
        },
        d = function (e) {
          let t = { ...i, ...e },
            r = (0, s.lazy)(() => t.loader().then(a)),
            d = t.loading;
          function c(e) {
            let a = d
                ? (0, l.jsx)(d, { isLoading: !0, pastDelay: !0, error: null })
                : null,
              i = t.ssr
                ? (0, l.jsxs)(l.Fragment, {
                    children: [
                      "undefined" == typeof window
                        ? (0, l.jsx)(o.PreloadCss, { moduleIds: t.modules })
                        : null,
                      (0, l.jsx)(r, { ...e }),
                    ],
                  })
                : (0, l.jsx)(n.BailoutToCSR, {
                    reason: "next/dynamic",
                    children: (0, l.jsx)(r, { ...e }),
                  });
            return (0, l.jsx)(s.Suspense, { fallback: a, children: i });
          }
          return ((c.displayName = "LoadableComponent"), c);
        };
    },
    1481: function (e, t, r) {
      "use strict";
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "PreloadCss", {
          enumerable: !0,
          get: function () {
            return n;
          },
        }));
      let l = r(7437),
        s = r(8512);
      function n(e) {
        let { moduleIds: t } = e;
        if ("undefined" != typeof window) return null;
        let r = (0, s.getExpectedRequestStore)("next/dynamic css"),
          n = [];
        if (r.reactLoadableManifest && t) {
          let e = r.reactLoadableManifest;
          for (let r of t) {
            if (!e[r]) continue;
            let t = e[r].files.filter((e) => e.endsWith(".css"));
            n.push(...t);
          }
        }
        return 0 === n.length
          ? null
          : (0, l.jsx)(l.Fragment, {
              children: n.map((e) =>
                (0, l.jsx)(
                  "link",
                  {
                    precedence: "dynamic",
                    rel: "stylesheet",
                    href: r.assetPrefix + "/_next/" + encodeURI(e),
                    as: "style",
                  },
                  e,
                ),
              ),
            });
      }
    },
    5550: function (e, t, r) {
      "use strict";
      r.d(t, {
        default: function () {
          return n;
        },
      });
      var l = r(7437);
      let s = (0, r(7818).default)(
        () =>
          Promise.all([
            r.e(689),
            r.e(582),
            r.e(878),
            r.e(918),
            r.e(325),
            r.e(422),
            r.e(746),
          ]).then(r.bind(r, 9746)),
        {
          loadableGenerated: { webpack: () => [9746] },
          ssr: !1,
          loading: () =>
            (0, l.jsx)("div", {
              className:
                "h-[calc(100vh-4.5rem)] flex flex-col items-center justify-center text-white",
              children: (0, l.jsx)("div", {
                className: "text-5xl animate-pulse opacity-20",
                children: "🎲",
              }),
            }),
        },
      );
      function n(e) {
        return (0, l.jsx)(s, { ...e });
      }
    },
    6168: function (e, t, r) {
      "use strict";
      r.d(t, {
        default: function () {
          return i;
        },
      });
      var l = r(7437),
        s = r(2265),
        n = r(5153),
        o = r(690),
        a = r(4392);
      function i() {
        let [e, t] = (0, s.useState)(!1),
          r = (0, n.T)("landing");
        return (0, l.jsxs)("div", {
          className:
            "\n        fixed bottom-4 left-4 right-4 z-50\n        rounded-xl overflow-hidden\n        backdrop-blur-md\n        transition-all duration-300 ease-in-out\n        ".concat(
              e ? "h-[70vh]" : "h-11",
              "\n      ",
            ),
          style: {
            background:
              "linear-gradient(180deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.06) 100%)",
            boxShadow:
              "0 4px 20px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.15)",
            border: "1px solid rgba(255,255,255,0.1)",
          },
          children: [
            (0, l.jsxs)("button", {
              onClick: () => t(!e),
              className:
                "w-full h-11 px-4 flex items-center justify-between transition-colors hover:bg-white/5",
              children: [
                (0, l.jsxs)("div", {
                  className: "flex items-center gap-2",
                  children: [
                    (0, l.jsx)(o.Z, { size: 16, className: "text-white/50" }),
                    (0, l.jsx)("span", {
                      className: "text-sm font-medium text-white/70",
                      children: r("infoBarTitle"),
                    }),
                  ],
                }),
                (0, l.jsx)(a.Z, {
                  size: 18,
                  className:
                    "text-white/50 transition-transform duration-300 ".concat(
                      e ? "rotate-180" : "",
                    ),
                }),
              ],
            }),
            (0, l.jsxs)("div", {
              className:
                "\n          overflow-y-auto\n          transition-all duration-300 ease-in-out\n          ".concat(
                  e
                    ? "h-[calc(70vh-2.75rem)] opacity-100"
                    : "h-0 opacity-0 overflow-hidden",
                  "\n        ",
                ),
              style: {
                background:
                  "linear-gradient(180deg, rgba(10,22,40,0.95) 0%, rgba(22,32,51,0.98) 100%)",
              },
              "aria-hidden": !e,
              children: [
                (0, l.jsxs)("section", {
                  className: "py-6 px-5 text-center border-t border-white/5",
                  children: [
                    (0, l.jsx)("h2", {
                      className:
                        "text-2xl md:text-3xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent",
                      children: r("heroTitle"),
                    }),
                    (0, l.jsx)("p", {
                      className: "text-base text-white/60 max-w-2xl mx-auto",
                      children: r("heroSubtitle"),
                    }),
                  ],
                }),
                (0, l.jsxs)("section", {
                  className: "py-6 px-5 max-w-6xl mx-auto",
                  children: [
                    (0, l.jsx)("h3", {
                      className:
                        "text-lg font-semibold text-center mb-5 text-white/80",
                      children: r("featuresTitle"),
                    }),
                    (0, l.jsxs)("div", {
                      className:
                        "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3",
                      children: [
                        (0, l.jsx)(d, {
                          icon: (0, l.jsx)("svg", {
                            className: "w-5 h-5",
                            fill: "none",
                            stroke: "currentColor",
                            viewBox: "0 0 24 24",
                            children: (0, l.jsx)("path", {
                              strokeLinecap: "round",
                              strokeLinejoin: "round",
                              strokeWidth: 2,
                              d: "M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5",
                            }),
                          }),
                          title: r("features.realistic.title"),
                          description: r("features.realistic.description"),
                        }),
                        (0, l.jsx)(d, {
                          icon: (0, l.jsx)("svg", {
                            className: "w-5 h-5",
                            fill: "none",
                            stroke: "currentColor",
                            viewBox: "0 0 24 24",
                            children: (0, l.jsx)("path", {
                              strokeLinecap: "round",
                              strokeLinejoin: "round",
                              strokeWidth: 2,
                              d: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4",
                            }),
                          }),
                          title: r("features.polyhedral.title"),
                          description: r("features.polyhedral.description"),
                        }),
                        (0, l.jsx)(d, {
                          icon: (0, l.jsx)("svg", {
                            className: "w-5 h-5",
                            fill: "none",
                            stroke: "currentColor",
                            viewBox: "0 0 24 24",
                            children: (0, l.jsx)("path", {
                              strokeLinecap: "round",
                              strokeLinejoin: "round",
                              strokeWidth: 2,
                              d: "M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414",
                            }),
                          }),
                          title: r("features.offline.title"),
                          description: r("features.offline.description"),
                        }),
                        (0, l.jsx)(d, {
                          icon: (0, l.jsx)("svg", {
                            className: "w-5 h-5",
                            fill: "none",
                            stroke: "currentColor",
                            viewBox: "0 0 24 24",
                            children: (0, l.jsx)("path", {
                              strokeLinecap: "round",
                              strokeLinejoin: "round",
                              strokeWidth: 2,
                              d: "M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z",
                            }),
                          }),
                          title: r("features.mobile.title"),
                          description: r("features.mobile.description"),
                        }),
                        (0, l.jsx)(d, {
                          icon: (0, l.jsx)("svg", {
                            className: "w-5 h-5",
                            fill: "none",
                            stroke: "currentColor",
                            viewBox: "0 0 24 24",
                            children: (0, l.jsx)("path", {
                              strokeLinecap: "round",
                              strokeLinejoin: "round",
                              strokeWidth: 2,
                              d: "M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10",
                            }),
                          }),
                          title: r("features.multiple.title"),
                          description: r("features.multiple.description"),
                        }),
                        (0, l.jsx)(d, {
                          icon: (0, l.jsx)("svg", {
                            className: "w-5 h-5",
                            fill: "none",
                            stroke: "currentColor",
                            viewBox: "0 0 24 24",
                            children: (0, l.jsx)("path", {
                              strokeLinecap: "round",
                              strokeLinejoin: "round",
                              strokeWidth: 2,
                              d: "M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01",
                            }),
                          }),
                          title: r("features.customization.title"),
                          description: r("features.customization.description"),
                        }),
                      ],
                    }),
                  ],
                }),
                (0, l.jsx)("section", {
                  className: "py-6 px-5 bg-black/20",
                  children: (0, l.jsxs)("div", {
                    className: "max-w-4xl mx-auto",
                    children: [
                      (0, l.jsx)("h3", {
                        className:
                          "text-lg font-semibold text-center mb-5 text-white/80",
                        children: r("howToUseTitle"),
                      }),
                      (0, l.jsxs)("div", {
                        className: "grid grid-cols-1 md:grid-cols-2 gap-3",
                        children: [
                          (0, l.jsx)(c, {
                            number: 1,
                            text: r("howToUse.step1"),
                          }),
                          (0, l.jsx)(c, {
                            number: 2,
                            text: r("howToUse.step2"),
                          }),
                          (0, l.jsx)(c, {
                            number: 3,
                            text: r("howToUse.step3"),
                          }),
                          (0, l.jsx)(c, {
                            number: 4,
                            text: r("howToUse.step4"),
                          }),
                        ],
                      }),
                    ],
                  }),
                }),
                (0, l.jsxs)("section", {
                  className: "py-6 px-5 max-w-4xl mx-auto",
                  children: [
                    (0, l.jsx)("h3", {
                      className:
                        "text-lg font-semibold text-center mb-5 text-white/80",
                      children: r("faqTitle"),
                    }),
                    (0, l.jsxs)("div", {
                      className: "space-y-3",
                      children: [
                        (0, l.jsx)(u, {
                          question: r("faq.q1"),
                          answer: r("faq.a1"),
                        }),
                        (0, l.jsx)(u, {
                          question: r("faq.q2"),
                          answer: r("faq.a2"),
                        }),
                        (0, l.jsx)(u, {
                          question: r("faq.q3"),
                          answer: r("faq.a3"),
                        }),
                        (0, l.jsx)(u, {
                          question: r("faq.q4"),
                          answer: r("faq.a4"),
                        }),
                      ],
                    }),
                  ],
                }),
                (0, l.jsxs)("nav", {
                  className: "py-6 px-5 bg-black/20",
                  children: [
                    (0, l.jsx)("h3", {
                      className:
                        "text-lg font-semibold text-center mb-5 text-white/80",
                      children: "More Tools",
                    }),
                    (0, l.jsxs)("div", {
                      className:
                        "flex flex-wrap gap-2 justify-center max-w-4xl mx-auto",
                      children: [
                        (0, l.jsx)("a", {
                          href: "/roll-d20",
                          className:
                            "text-xs px-3 py-1.5 rounded-full text-blue-400/80 hover:text-blue-300 transition-colors",
                          style: {
                            background: "rgba(59,130,246,0.1)",
                            border: "1px solid rgba(59,130,246,0.15)",
                          },
                          children: "Roll D20",
                        }),
                        (0, l.jsx)("a", {
                          href: "/roll-d6",
                          className:
                            "text-xs px-3 py-1.5 rounded-full text-blue-400/80 hover:text-blue-300 transition-colors",
                          style: {
                            background: "rgba(59,130,246,0.1)",
                            border: "1px solid rgba(59,130,246,0.15)",
                          },
                          children: "Roll a Die",
                        }),
                        (0, l.jsx)("a", {
                          href: "/roll-2d6",
                          className:
                            "text-xs px-3 py-1.5 rounded-full text-blue-400/80 hover:text-blue-300 transition-colors",
                          style: {
                            background: "rgba(59,130,246,0.1)",
                            border: "1px solid rgba(59,130,246,0.15)",
                          },
                          children: "Roll 2D6",
                        }),
                        (0, l.jsx)("a", {
                          href: "/dnd-dice-roller",
                          className:
                            "text-xs px-3 py-1.5 rounded-full text-blue-400/80 hover:text-blue-300 transition-colors",
                          style: {
                            background: "rgba(59,130,246,0.1)",
                            border: "1px solid rgba(59,130,246,0.15)",
                          },
                          children: "D&D Dice Roller",
                        }),
                        (0, l.jsx)("a", {
                          href: "/roll-4d6-drop-lowest",
                          className:
                            "text-xs px-3 py-1.5 rounded-full text-blue-400/80 hover:text-blue-300 transition-colors",
                          style: {
                            background: "rgba(59,130,246,0.1)",
                            border: "1px solid rgba(59,130,246,0.15)",
                          },
                          children: "4d6 Drop Lowest",
                        }),
                        (0, l.jsx)("a", {
                          href: "/flip-a-coin",
                          className:
                            "text-xs px-3 py-1.5 rounded-full text-blue-400/80 hover:text-blue-300 transition-colors",
                          style: {
                            background: "rgba(59,130,246,0.1)",
                            border: "1px solid rgba(59,130,246,0.15)",
                          },
                          children: "Flip a Coin",
                        }),
                        (0, l.jsx)("a", {
                          href: "/random-number-generator",
                          className:
                            "text-xs px-3 py-1.5 rounded-full text-blue-400/80 hover:text-blue-300 transition-colors",
                          style: {
                            background: "rgba(59,130,246,0.1)",
                            border: "1px solid rgba(59,130,246,0.15)",
                          },
                          children: "Random Number Generator",
                        }),
                        (0, l.jsx)("a", {
                          href: "/dnd-tools",
                          className:
                            "text-xs px-3 py-1.5 rounded-full text-blue-400/80 hover:text-blue-300 transition-colors",
                          style: {
                            background: "rgba(59,130,246,0.1)",
                            border: "1px solid rgba(59,130,246,0.15)",
                          },
                          children: "D&D Tools",
                        }),
                        (0, l.jsx)("a", {
                          href: "/yahtzee-scorecard",
                          className:
                            "text-xs px-3 py-1.5 rounded-full text-blue-400/80 hover:text-blue-300 transition-colors",
                          style: {
                            background: "rgba(59,130,246,0.1)",
                            border: "1px solid rgba(59,130,246,0.15)",
                          },
                          children: "Yahtzee Scorecard",
                        }),
                        (0, l.jsx)("a", {
                          href: "/score-counter",
                          className:
                            "text-xs px-3 py-1.5 rounded-full text-blue-400/80 hover:text-blue-300 transition-colors",
                          style: {
                            background: "rgba(59,130,246,0.1)",
                            border: "1px solid rgba(59,130,246,0.15)",
                          },
                          children: "Score Counter",
                        }),
                        (0, l.jsx)("a", {
                          href: "/dice-probability-calculator",
                          className:
                            "text-xs px-3 py-1.5 rounded-full text-blue-400/80 hover:text-blue-300 transition-colors",
                          style: {
                            background: "rgba(59,130,246,0.1)",
                            border: "1px solid rgba(59,130,246,0.15)",
                          },
                          children: "Dice Probability Calculator",
                        }),
                      ],
                    }),
                  ],
                }),
                (0, l.jsx)("div", { className: "h-6" }),
              ],
            }),
          ],
        });
      }
      function d(e) {
        let { icon: t, title: r, description: s } = e;
        return (0, l.jsxs)("div", {
          className: "rounded-lg p-3 transition-colors hover:bg-white/5",
          style: {
            background:
              "linear-gradient(180deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.04) 100%)",
            border: "1px solid rgba(255,255,255,0.06)",
          },
          children: [
            (0, l.jsx)("div", {
              className: "text-blue-400/80 mb-1.5",
              children: t,
            }),
            (0, l.jsx)("h4", {
              className: "text-sm font-semibold mb-0.5 text-white/90",
              children: r,
            }),
            (0, l.jsx)("p", {
              className: "text-xs text-white/50 leading-relaxed",
              children: s,
            }),
          ],
        });
      }
      function c(e) {
        let { number: t, text: r } = e;
        return (0, l.jsxs)("div", {
          className: "flex items-start gap-3 rounded-lg p-3",
          style: {
            background:
              "linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.03) 100%)",
            border: "1px solid rgba(255,255,255,0.05)",
          },
          children: [
            (0, l.jsx)("div", {
              className:
                "flex-shrink-0 w-7 h-7 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center font-bold text-xs shadow-lg",
              children: t,
            }),
            (0, l.jsx)("p", {
              className: "text-sm text-white/60 pt-0.5",
              children: r,
            }),
          ],
        });
      }
      function u(e) {
        let { question: t, answer: r } = e;
        return (0, l.jsxs)("div", {
          className: "rounded-lg p-3",
          style: {
            background:
              "linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.03) 100%)",
            border: "1px solid rgba(255,255,255,0.05)",
          },
          children: [
            (0, l.jsx)("h4", {
              className: "text-sm font-semibold mb-1 text-blue-400/90",
              children: t,
            }),
            (0, l.jsx)("p", {
              className: "text-xs text-white/50 leading-relaxed",
              children: r,
            }),
          ],
        });
      }
    },
    5153: function (e, t, r) {
      "use strict";
      r.d(t, {
        T: function () {
          return n;
        },
      });
      var l = r(2756);
      function s(e, t) {
        return (...e) => {
          try {
            return t(...e);
          } catch {
            throw Error(void 0);
          }
        };
      }
      let n = s(0, l.T_);
      s(0, l.Gb);
    },
  },
]);
