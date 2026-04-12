"use strict";
(self.webpackChunk_N_E = self.webpackChunk_N_E || []).push([
  [879],
  {
    6463: function (e, t, r) {
      var n = r(1169);
      (r.o(n, "useParams") &&
        r.d(t, {
          useParams: function () {
            return n.useParams;
          },
        }),
        r.o(n, "usePathname") &&
          r.d(t, {
            usePathname: function () {
              return n.usePathname;
            },
          }),
        r.o(n, "useSearchParams") &&
          r.d(t, {
            useSearchParams: function () {
              return n.useSearchParams;
            },
          }));
    },
    844: function (e, t, r) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "addLocale", {
          enumerable: !0,
          get: function () {
            return n;
          },
        }),
        r(8157));
      let n = function (e) {
        for (
          var t = arguments.length, r = Array(t > 1 ? t - 1 : 0), n = 1;
          n < t;
          n++
        )
          r[n - 1] = arguments[n];
        return e;
      };
      ("function" == typeof t.default ||
        ("object" == typeof t.default && null !== t.default)) &&
        void 0 === t.default.__esModule &&
        (Object.defineProperty(t.default, "__esModule", { value: !0 }),
        Object.assign(t.default, t),
        (e.exports = t.default));
    },
    5944: function (e, t, r) {
      function n(e, t, r, n) {
        return !1;
      }
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "getDomainLocale", {
          enumerable: !0,
          get: function () {
            return n;
          },
        }),
        r(8157),
        ("function" == typeof t.default ||
          ("object" == typeof t.default && null !== t.default)) &&
          void 0 === t.default.__esModule &&
          (Object.defineProperty(t.default, "__esModule", { value: !0 }),
          Object.assign(t.default, t),
          (e.exports = t.default)));
    },
    231: function (e, t, r) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "default", {
          enumerable: !0,
          get: function () {
            return T;
          },
        }));
      let n = r(9920),
        i = r(7437),
        o = n._(r(2265)),
        s = r(8016),
        a = r(8029),
        l = r(1142),
        u = r(3461),
        h = r(844),
        c = r(291),
        f = r(4467),
        m = r(3106),
        p = r(5944),
        d = r(4897),
        g = r(1507),
        E = new Set();
      function b(e, t, r, n, i, o) {
        if ("undefined" != typeof window && (o || (0, a.isLocalURL)(t))) {
          if (!n.bypassPrefetchedCheck) {
            let i =
              t +
              "%" +
              r +
              "%" +
              (void 0 !== n.locale
                ? n.locale
                : "locale" in e
                  ? e.locale
                  : void 0);
            if (E.has(i)) return;
            E.add(i);
          }
          (async () => (o ? e.prefetch(t, i) : e.prefetch(t, r, n)))().catch(
            (e) => {},
          );
        }
      }
      function y(e) {
        return "string" == typeof e ? e : (0, l.formatUrl)(e);
      }
      let T = o.default.forwardRef(function (e, t) {
        let r, n;
        let {
          href: l,
          as: E,
          children: T,
          prefetch: _ = null,
          passHref: H,
          replace: P,
          shallow: S,
          scroll: A,
          locale: N,
          onClick: B,
          onMouseEnter: R,
          onTouchStart: I,
          legacyBehavior: M = !1,
          ...L
        } = e;
        ((r = T),
          M &&
            ("string" == typeof r || "number" == typeof r) &&
            (r = (0, i.jsx)("a", { children: r })));
        let O = o.default.useContext(c.RouterContext),
          v = o.default.useContext(f.AppRouterContext),
          C = null != O ? O : v,
          w = !O,
          U = !1 !== _,
          G = null === _ ? g.PrefetchKind.AUTO : g.PrefetchKind.FULL,
          { href: D, as: F } = o.default.useMemo(() => {
            if (!O) {
              let e = y(l);
              return { href: e, as: E ? y(E) : e };
            }
            let [e, t] = (0, s.resolveHref)(O, l, !0);
            return { href: e, as: E ? (0, s.resolveHref)(O, E) : t || e };
          }, [O, l, E]),
          k = o.default.useRef(D),
          j = o.default.useRef(F);
        M && (n = o.default.Children.only(r));
        let x = M ? n && "object" == typeof n && n.ref : t,
          [V, K, X] = (0, m.useIntersection)({ rootMargin: "200px" }),
          Z = o.default.useCallback(
            (e) => {
              ((j.current !== F || k.current !== D) &&
                (X(), (j.current = F), (k.current = D)),
                V(e),
                x &&
                  ("function" == typeof x
                    ? x(e)
                    : "object" == typeof x && (x.current = e)));
            },
            [F, x, D, X, V],
          );
        o.default.useEffect(() => {
          C && K && U && b(C, D, F, { locale: N }, { kind: G }, w);
        }, [F, D, K, N, U, null == O ? void 0 : O.locale, C, w, G]);
        let W = {
          ref: Z,
          onClick(e) {
            (M || "function" != typeof B || B(e),
              M &&
                n.props &&
                "function" == typeof n.props.onClick &&
                n.props.onClick(e),
              C &&
                !e.defaultPrevented &&
                (function (e, t, r, n, i, s, l, u, h) {
                  let { nodeName: c } = e.currentTarget;
                  if (
                    "A" === c.toUpperCase() &&
                    ((function (e) {
                      let t = e.currentTarget.getAttribute("target");
                      return (
                        (t && "_self" !== t) ||
                        e.metaKey ||
                        e.ctrlKey ||
                        e.shiftKey ||
                        e.altKey ||
                        (e.nativeEvent && 2 === e.nativeEvent.which)
                      );
                    })(e) ||
                      (!h && !(0, a.isLocalURL)(r)))
                  )
                    return;
                  e.preventDefault();
                  let f = () => {
                    let e = null == l || l;
                    "beforePopState" in t
                      ? t[i ? "replace" : "push"](r, n, {
                          shallow: s,
                          locale: u,
                          scroll: e,
                        })
                      : t[i ? "replace" : "push"](n || r, { scroll: e });
                  };
                  h ? o.default.startTransition(f) : f();
                })(e, C, D, F, P, S, A, N, w));
          },
          onMouseEnter(e) {
            (M || "function" != typeof R || R(e),
              M &&
                n.props &&
                "function" == typeof n.props.onMouseEnter &&
                n.props.onMouseEnter(e),
              C &&
                (U || !w) &&
                b(
                  C,
                  D,
                  F,
                  { locale: N, priority: !0, bypassPrefetchedCheck: !0 },
                  { kind: G },
                  w,
                ));
          },
          onTouchStart: function (e) {
            (M || "function" != typeof I || I(e),
              M &&
                n.props &&
                "function" == typeof n.props.onTouchStart &&
                n.props.onTouchStart(e),
              C &&
                (U || !w) &&
                b(
                  C,
                  D,
                  F,
                  { locale: N, priority: !0, bypassPrefetchedCheck: !0 },
                  { kind: G },
                  w,
                ));
          },
        };
        if ((0, u.isAbsoluteUrl)(F)) W.href = F;
        else if (!M || H || ("a" === n.type && !("href" in n.props))) {
          let e = void 0 !== N ? N : null == O ? void 0 : O.locale,
            t =
              (null == O ? void 0 : O.isLocaleDomain) &&
              (0, p.getDomainLocale)(
                F,
                e,
                null == O ? void 0 : O.locales,
                null == O ? void 0 : O.domainLocales,
              );
          W.href =
            t ||
            (0, d.addBasePath)(
              (0, h.addLocale)(F, e, null == O ? void 0 : O.defaultLocale),
            );
        }
        return M
          ? o.default.cloneElement(n, W)
          : (0, i.jsx)("a", { ...L, ...W, children: r });
      });
      ("function" == typeof t.default ||
        ("object" == typeof t.default && null !== t.default)) &&
        void 0 === t.default.__esModule &&
        (Object.defineProperty(t.default, "__esModule", { value: !0 }),
        Object.assign(t.default, t),
        (e.exports = t.default));
    },
    9189: function (e, t) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        (function (e, t) {
          for (var r in t)
            Object.defineProperty(e, r, { enumerable: !0, get: t[r] });
        })(t, {
          cancelIdleCallback: function () {
            return n;
          },
          requestIdleCallback: function () {
            return r;
          },
        }));
      let r =
          ("undefined" != typeof self &&
            self.requestIdleCallback &&
            self.requestIdleCallback.bind(window)) ||
          function (e) {
            let t = Date.now();
            return self.setTimeout(function () {
              e({
                didTimeout: !1,
                timeRemaining: function () {
                  return Math.max(0, 50 - (Date.now() - t));
                },
              });
            }, 1);
          },
        n =
          ("undefined" != typeof self &&
            self.cancelIdleCallback &&
            self.cancelIdleCallback.bind(window)) ||
          function (e) {
            return clearTimeout(e);
          };
      ("function" == typeof t.default ||
        ("object" == typeof t.default && null !== t.default)) &&
        void 0 === t.default.__esModule &&
        (Object.defineProperty(t.default, "__esModule", { value: !0 }),
        Object.assign(t.default, t),
        (e.exports = t.default));
    },
    8016: function (e, t, r) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "resolveHref", {
          enumerable: !0,
          get: function () {
            return c;
          },
        }));
      let n = r(8323),
        i = r(1142),
        o = r(5519),
        s = r(3461),
        a = r(8157),
        l = r(8029),
        u = r(9195),
        h = r(20);
      function c(e, t, r) {
        let c;
        let f = "string" == typeof t ? t : (0, i.formatWithValidation)(t),
          m = f.match(/^[a-zA-Z]{1,}:\/\//),
          p = m ? f.slice(m[0].length) : f;
        if ((p.split("?", 1)[0] || "").match(/(\/\/|\\)/)) {
          console.error(
            "Invalid href '" +
              f +
              "' passed to next/router in page: '" +
              e.pathname +
              "'. Repeated forward-slashes (//) or backslashes \\ are not valid in the href.",
          );
          let t = (0, s.normalizeRepeatedSlashes)(p);
          f = (m ? m[0] : "") + t;
        }
        if (!(0, l.isLocalURL)(f)) return r ? [f] : f;
        try {
          c = new URL(f.startsWith("#") ? e.asPath : e.pathname, "http://n");
        } catch (e) {
          c = new URL("/", "http://n");
        }
        try {
          let e = new URL(f, c);
          e.pathname = (0, a.normalizePathTrailingSlash)(e.pathname);
          let t = "";
          if ((0, u.isDynamicRoute)(e.pathname) && e.searchParams && r) {
            let r = (0, n.searchParamsToUrlQuery)(e.searchParams),
              { result: s, params: a } = (0, h.interpolateAs)(
                e.pathname,
                e.pathname,
                r,
              );
            s &&
              (t = (0, i.formatWithValidation)({
                pathname: s,
                hash: e.hash,
                query: (0, o.omit)(r, a),
              }));
          }
          let s =
            e.origin === c.origin ? e.href.slice(e.origin.length) : e.href;
          return r ? [s, t || s] : s;
        } catch (e) {
          return r ? [f] : f;
        }
      }
      ("function" == typeof t.default ||
        ("object" == typeof t.default && null !== t.default)) &&
        void 0 === t.default.__esModule &&
        (Object.defineProperty(t.default, "__esModule", { value: !0 }),
        Object.assign(t.default, t),
        (e.exports = t.default));
    },
    3106: function (e, t, r) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "useIntersection", {
          enumerable: !0,
          get: function () {
            return l;
          },
        }));
      let n = r(2265),
        i = r(9189),
        o = "function" == typeof IntersectionObserver,
        s = new Map(),
        a = [];
      function l(e) {
        let { rootRef: t, rootMargin: r, disabled: l } = e,
          u = l || !o,
          [h, c] = (0, n.useState)(!1),
          f = (0, n.useRef)(null),
          m = (0, n.useCallback)((e) => {
            f.current = e;
          }, []);
        return (
          (0, n.useEffect)(() => {
            if (o) {
              if (u || h) return;
              let e = f.current;
              if (e && e.tagName)
                return (function (e, t, r) {
                  let {
                    id: n,
                    observer: i,
                    elements: o,
                  } = (function (e) {
                    let t;
                    let r = {
                        root: e.root || null,
                        margin: e.rootMargin || "",
                      },
                      n = a.find(
                        (e) => e.root === r.root && e.margin === r.margin,
                      );
                    if (n && (t = s.get(n))) return t;
                    let i = new Map();
                    return (
                      (t = {
                        id: r,
                        observer: new IntersectionObserver((e) => {
                          e.forEach((e) => {
                            let t = i.get(e.target),
                              r = e.isIntersecting || e.intersectionRatio > 0;
                            t && r && t(r);
                          });
                        }, e),
                        elements: i,
                      }),
                      a.push(r),
                      s.set(r, t),
                      t
                    );
                  })(r);
                  return (
                    o.set(e, t),
                    i.observe(e),
                    function () {
                      if ((o.delete(e), i.unobserve(e), 0 === o.size)) {
                        (i.disconnect(), s.delete(n));
                        let e = a.findIndex(
                          (e) => e.root === n.root && e.margin === n.margin,
                        );
                        e > -1 && a.splice(e, 1);
                      }
                    }
                  );
                })(e, (e) => e && c(e), {
                  root: null == t ? void 0 : t.current,
                  rootMargin: r,
                });
            } else if (!h) {
              let e = (0, i.requestIdleCallback)(() => c(!0));
              return () => (0, i.cancelIdleCallback)(e);
            }
          }, [u, r, t, h, f.current]),
          [
            m,
            h,
            (0, n.useCallback)(() => {
              c(!1);
            }, []),
          ]
        );
      }
      ("function" == typeof t.default ||
        ("object" == typeof t.default && null !== t.default)) &&
        void 0 === t.default.__esModule &&
        (Object.defineProperty(t.default, "__esModule", { value: !0 }),
        Object.assign(t.default, t),
        (e.exports = t.default));
    },
    1943: function (e, t) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "escapeStringRegexp", {
          enumerable: !0,
          get: function () {
            return i;
          },
        }));
      let r = /[|\\{}()[\]^$+*?.-]/,
        n = /[|\\{}()[\]^$+*?.-]/g;
      function i(e) {
        return r.test(e) ? e.replace(n, "\\$&") : e;
      }
    },
    291: function (e, t, r) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "RouterContext", {
          enumerable: !0,
          get: function () {
            return n;
          },
        }));
      let n = r(9920)._(r(2265)).default.createContext(null);
    },
    1142: function (e, t, r) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        (function (e, t) {
          for (var r in t)
            Object.defineProperty(e, r, { enumerable: !0, get: t[r] });
        })(t, {
          formatUrl: function () {
            return o;
          },
          formatWithValidation: function () {
            return a;
          },
          urlObjectKeys: function () {
            return s;
          },
        }));
      let n = r(1452)._(r(8323)),
        i = /https?|ftp|gopher|file/;
      function o(e) {
        let { auth: t, hostname: r } = e,
          o = e.protocol || "",
          s = e.pathname || "",
          a = e.hash || "",
          l = e.query || "",
          u = !1;
        ((t = t ? encodeURIComponent(t).replace(/%3A/i, ":") + "@" : ""),
          e.host
            ? (u = t + e.host)
            : r &&
              ((u = t + (~r.indexOf(":") ? "[" + r + "]" : r)),
              e.port && (u += ":" + e.port)),
          l &&
            "object" == typeof l &&
            (l = String(n.urlQueryToSearchParams(l))));
        let h = e.search || (l && "?" + l) || "";
        return (
          o && !o.endsWith(":") && (o += ":"),
          e.slashes || ((!o || i.test(o)) && !1 !== u)
            ? ((u = "//" + (u || "")), s && "/" !== s[0] && (s = "/" + s))
            : u || (u = ""),
          a && "#" !== a[0] && (a = "#" + a),
          h && "?" !== h[0] && (h = "?" + h),
          "" +
            o +
            u +
            (s = s.replace(/[?#]/g, encodeURIComponent)) +
            (h = h.replace("#", "%23")) +
            a
        );
      }
      let s = [
        "auth",
        "hash",
        "host",
        "hostname",
        "href",
        "path",
        "pathname",
        "port",
        "protocol",
        "query",
        "search",
        "slashes",
      ];
      function a(e) {
        return o(e);
      }
    },
    9195: function (e, t, r) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        (function (e, t) {
          for (var r in t)
            Object.defineProperty(e, r, { enumerable: !0, get: t[r] });
        })(t, {
          getSortedRoutes: function () {
            return n.getSortedRoutes;
          },
          isDynamicRoute: function () {
            return i.isDynamicRoute;
          },
        }));
      let n = r(9089),
        i = r(8083);
    },
    20: function (e, t, r) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "interpolateAs", {
          enumerable: !0,
          get: function () {
            return o;
          },
        }));
      let n = r(1533),
        i = r(3169);
      function o(e, t, r) {
        let o = "",
          s = (0, i.getRouteRegex)(e),
          a = s.groups,
          l = (t !== e ? (0, n.getRouteMatcher)(s)(t) : "") || r;
        o = e;
        let u = Object.keys(a);
        return (
          u.every((e) => {
            let t = l[e] || "",
              { repeat: r, optional: n } = a[e],
              i = "[" + (r ? "..." : "") + e + "]";
            return (
              n && (i = (t ? "" : "/") + "[" + i + "]"),
              r && !Array.isArray(t) && (t = [t]),
              (n || e in l) &&
                (o =
                  o.replace(
                    i,
                    r
                      ? t.map((e) => encodeURIComponent(e)).join("/")
                      : encodeURIComponent(t),
                  ) || "/")
            );
          }) || (o = ""),
          { params: u, result: o }
        );
      }
    },
    8083: function (e, t, r) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "isDynamicRoute", {
          enumerable: !0,
          get: function () {
            return o;
          },
        }));
      let n = r(2269),
        i = /\/\[[^/]+?\](?=\/|$)/;
      function o(e) {
        return (
          (0, n.isInterceptionRouteAppPath)(e) &&
            (e = (0, n.extractInterceptionRouteInformation)(
              e,
            ).interceptedRoute),
          i.test(e)
        );
      }
    },
    8029: function (e, t, r) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "isLocalURL", {
          enumerable: !0,
          get: function () {
            return o;
          },
        }));
      let n = r(3461),
        i = r(9404);
      function o(e) {
        if (!(0, n.isAbsoluteUrl)(e)) return !0;
        try {
          let t = (0, n.getLocationOrigin)(),
            r = new URL(e, t);
          return r.origin === t && (0, i.hasBasePath)(r.pathname);
        } catch (e) {
          return !1;
        }
      }
    },
    5519: function (e, t) {
      function r(e, t) {
        let r = {};
        return (
          Object.keys(e).forEach((n) => {
            t.includes(n) || (r[n] = e[n]);
          }),
          r
        );
      }
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "omit", {
          enumerable: !0,
          get: function () {
            return r;
          },
        }));
    },
    8323: function (e, t) {
      function r(e) {
        let t = {};
        return (
          e.forEach((e, r) => {
            void 0 === t[r]
              ? (t[r] = e)
              : Array.isArray(t[r])
                ? t[r].push(e)
                : (t[r] = [t[r], e]);
          }),
          t
        );
      }
      function n(e) {
        return "string" != typeof e &&
          ("number" != typeof e || isNaN(e)) &&
          "boolean" != typeof e
          ? ""
          : String(e);
      }
      function i(e) {
        let t = new URLSearchParams();
        return (
          Object.entries(e).forEach((e) => {
            let [r, i] = e;
            Array.isArray(i)
              ? i.forEach((e) => t.append(r, n(e)))
              : t.set(r, n(i));
          }),
          t
        );
      }
      function o(e) {
        for (
          var t = arguments.length, r = Array(t > 1 ? t - 1 : 0), n = 1;
          n < t;
          n++
        )
          r[n - 1] = arguments[n];
        return (
          r.forEach((t) => {
            (Array.from(t.keys()).forEach((t) => e.delete(t)),
              t.forEach((t, r) => e.append(r, t)));
          }),
          e
        );
      }
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        (function (e, t) {
          for (var r in t)
            Object.defineProperty(e, r, { enumerable: !0, get: t[r] });
        })(t, {
          assign: function () {
            return o;
          },
          searchParamsToUrlQuery: function () {
            return r;
          },
          urlQueryToSearchParams: function () {
            return i;
          },
        }));
    },
    1533: function (e, t, r) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "getRouteMatcher", {
          enumerable: !0,
          get: function () {
            return i;
          },
        }));
      let n = r(3461);
      function i(e) {
        let { re: t, groups: r } = e;
        return (e) => {
          let i = t.exec(e);
          if (!i) return !1;
          let o = (e) => {
              try {
                return decodeURIComponent(e);
              } catch (e) {
                throw new n.DecodeError("failed to decode param");
              }
            },
            s = {};
          return (
            Object.keys(r).forEach((e) => {
              let t = r[e],
                n = i[t.pos];
              void 0 !== n &&
                (s[e] = ~n.indexOf("/")
                  ? n.split("/").map((e) => o(e))
                  : t.repeat
                    ? [o(n)]
                    : o(n));
            }),
            s
          );
        };
      }
    },
    3169: function (e, t, r) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        (function (e, t) {
          for (var r in t)
            Object.defineProperty(e, r, { enumerable: !0, get: t[r] });
        })(t, {
          getNamedMiddlewareRegex: function () {
            return f;
          },
          getNamedRouteRegex: function () {
            return c;
          },
          getRouteRegex: function () {
            return l;
          },
        }));
      let n = r(2269),
        i = r(1943),
        o = r(7741);
      function s(e) {
        let t = e.startsWith("[") && e.endsWith("]");
        t && (e = e.slice(1, -1));
        let r = e.startsWith("...");
        return (r && (e = e.slice(3)), { key: e, repeat: r, optional: t });
      }
      function a(e) {
        let t = (0, o.removeTrailingSlash)(e).slice(1).split("/"),
          r = {},
          a = 1;
        return {
          parameterizedRoute: t
            .map((e) => {
              let t = n.INTERCEPTION_ROUTE_MARKERS.find((t) => e.startsWith(t)),
                o = e.match(/\[((?:\[.*\])|.+)\]/);
              if (t && o) {
                let { key: e, optional: n, repeat: l } = s(o[1]);
                return (
                  (r[e] = { pos: a++, repeat: l, optional: n }),
                  "/" + (0, i.escapeStringRegexp)(t) + "([^/]+?)"
                );
              }
              if (!o) return "/" + (0, i.escapeStringRegexp)(e);
              {
                let { key: e, repeat: t, optional: n } = s(o[1]);
                return (
                  (r[e] = { pos: a++, repeat: t, optional: n }),
                  t ? (n ? "(?:/(.+?))?" : "/(.+?)") : "/([^/]+?)"
                );
              }
            })
            .join(""),
          groups: r,
        };
      }
      function l(e) {
        let { parameterizedRoute: t, groups: r } = a(e);
        return { re: RegExp("^" + t + "(?:/)?$"), groups: r };
      }
      function u(e) {
        let {
            interceptionMarker: t,
            getSafeRouteKey: r,
            segment: n,
            routeKeys: o,
            keyPrefix: a,
          } = e,
          { key: l, optional: u, repeat: h } = s(n),
          c = l.replace(/\W/g, "");
        a && (c = "" + a + c);
        let f = !1;
        ((0 === c.length || c.length > 30) && (f = !0),
          isNaN(parseInt(c.slice(0, 1))) || (f = !0),
          f && (c = r()),
          a ? (o[c] = "" + a + l) : (o[c] = l));
        let m = t ? (0, i.escapeStringRegexp)(t) : "";
        return h
          ? u
            ? "(?:/" + m + "(?<" + c + ">.+?))?"
            : "/" + m + "(?<" + c + ">.+?)"
          : "/" + m + "(?<" + c + ">[^/]+?)";
      }
      function h(e, t) {
        let r;
        let s = (0, o.removeTrailingSlash)(e).slice(1).split("/"),
          a =
            ((r = 0),
            () => {
              let e = "",
                t = ++r;
              for (; t > 0; )
                ((e += String.fromCharCode(97 + ((t - 1) % 26))),
                  (t = Math.floor((t - 1) / 26)));
              return e;
            }),
          l = {};
        return {
          namedParameterizedRoute: s
            .map((e) => {
              let r = n.INTERCEPTION_ROUTE_MARKERS.some((t) => e.startsWith(t)),
                o = e.match(/\[((?:\[.*\])|.+)\]/);
              if (r && o) {
                let [r] = e.split(o[0]);
                return u({
                  getSafeRouteKey: a,
                  interceptionMarker: r,
                  segment: o[1],
                  routeKeys: l,
                  keyPrefix: t ? "nxtI" : void 0,
                });
              }
              return o
                ? u({
                    getSafeRouteKey: a,
                    segment: o[1],
                    routeKeys: l,
                    keyPrefix: t ? "nxtP" : void 0,
                  })
                : "/" + (0, i.escapeStringRegexp)(e);
            })
            .join(""),
          routeKeys: l,
        };
      }
      function c(e, t) {
        let r = h(e, t);
        return {
          ...l(e),
          namedRegex: "^" + r.namedParameterizedRoute + "(?:/)?$",
          routeKeys: r.routeKeys,
        };
      }
      function f(e, t) {
        let { parameterizedRoute: r } = a(e),
          { catchAll: n = !0 } = t;
        if ("/" === r) return { namedRegex: "^/" + (n ? ".*" : "") + "$" };
        let { namedParameterizedRoute: i } = h(e, !1);
        return { namedRegex: "^" + i + (n ? "(?:(/.*)?)" : "") + "$" };
      }
    },
    9089: function (e, t) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        Object.defineProperty(t, "getSortedRoutes", {
          enumerable: !0,
          get: function () {
            return n;
          },
        }));
      class r {
        insert(e) {
          this._insert(e.split("/").filter(Boolean), [], !1);
        }
        smoosh() {
          return this._smoosh();
        }
        _smoosh(e) {
          void 0 === e && (e = "/");
          let t = [...this.children.keys()].sort();
          (null !== this.slugName && t.splice(t.indexOf("[]"), 1),
            null !== this.restSlugName && t.splice(t.indexOf("[...]"), 1),
            null !== this.optionalRestSlugName &&
              t.splice(t.indexOf("[[...]]"), 1));
          let r = t
            .map((t) => this.children.get(t)._smoosh("" + e + t + "/"))
            .reduce((e, t) => [...e, ...t], []);
          if (
            (null !== this.slugName &&
              r.push(
                ...this.children
                  .get("[]")
                  ._smoosh(e + "[" + this.slugName + "]/"),
              ),
            !this.placeholder)
          ) {
            let t = "/" === e ? "/" : e.slice(0, -1);
            if (null != this.optionalRestSlugName)
              throw Error(
                'You cannot define a route with the same specificity as a optional catch-all route ("' +
                  t +
                  '" and "' +
                  t +
                  "[[..." +
                  this.optionalRestSlugName +
                  ']]").',
              );
            r.unshift(t);
          }
          return (
            null !== this.restSlugName &&
              r.push(
                ...this.children
                  .get("[...]")
                  ._smoosh(e + "[..." + this.restSlugName + "]/"),
              ),
            null !== this.optionalRestSlugName &&
              r.push(
                ...this.children
                  .get("[[...]]")
                  ._smoosh(e + "[[..." + this.optionalRestSlugName + "]]/"),
              ),
            r
          );
        }
        _insert(e, t, n) {
          if (0 === e.length) {
            this.placeholder = !1;
            return;
          }
          if (n) throw Error("Catch-all must be the last part of the URL.");
          let i = e[0];
          if (i.startsWith("[") && i.endsWith("]")) {
            let r = i.slice(1, -1),
              s = !1;
            if (
              (r.startsWith("[") &&
                r.endsWith("]") &&
                ((r = r.slice(1, -1)), (s = !0)),
              r.startsWith("...") && ((r = r.substring(3)), (n = !0)),
              r.startsWith("[") || r.endsWith("]"))
            )
              throw Error(
                "Segment names may not start or end with extra brackets ('" +
                  r +
                  "').",
              );
            if (r.startsWith("."))
              throw Error(
                "Segment names may not start with erroneous periods ('" +
                  r +
                  "').",
              );
            function o(e, r) {
              if (null !== e && e !== r)
                throw Error(
                  "You cannot use different slug names for the same dynamic path ('" +
                    e +
                    "' !== '" +
                    r +
                    "').",
                );
              (t.forEach((e) => {
                if (e === r)
                  throw Error(
                    'You cannot have the same slug name "' +
                      r +
                      '" repeat within a single dynamic path',
                  );
                if (e.replace(/\W/g, "") === i.replace(/\W/g, ""))
                  throw Error(
                    'You cannot have the slug names "' +
                      e +
                      '" and "' +
                      r +
                      '" differ only by non-word symbols within a single dynamic path',
                  );
              }),
                t.push(r));
            }
            if (n) {
              if (s) {
                if (null != this.restSlugName)
                  throw Error(
                    'You cannot use both an required and optional catch-all route at the same level ("[...' +
                      this.restSlugName +
                      ']" and "' +
                      e[0] +
                      '" ).',
                  );
                (o(this.optionalRestSlugName, r),
                  (this.optionalRestSlugName = r),
                  (i = "[[...]]"));
              } else {
                if (null != this.optionalRestSlugName)
                  throw Error(
                    'You cannot use both an optional and required catch-all route at the same level ("[[...' +
                      this.optionalRestSlugName +
                      ']]" and "' +
                      e[0] +
                      '").',
                  );
                (o(this.restSlugName, r),
                  (this.restSlugName = r),
                  (i = "[...]"));
              }
            } else {
              if (s)
                throw Error(
                  'Optional route parameters are not yet supported ("' +
                    e[0] +
                    '").',
                );
              (o(this.slugName, r), (this.slugName = r), (i = "[]"));
            }
          }
          (this.children.has(i) || this.children.set(i, new r()),
            this.children.get(i)._insert(e.slice(1), t, n));
        }
        constructor() {
          ((this.placeholder = !0),
            (this.children = new Map()),
            (this.slugName = null),
            (this.restSlugName = null),
            (this.optionalRestSlugName = null));
        }
      }
      function n(e) {
        let t = new r();
        return (e.forEach((e) => t.insert(e)), t.smoosh());
      }
    },
    3461: function (e, t) {
      (Object.defineProperty(t, "__esModule", { value: !0 }),
        (function (e, t) {
          for (var r in t)
            Object.defineProperty(e, r, { enumerable: !0, get: t[r] });
        })(t, {
          DecodeError: function () {
            return p;
          },
          MiddlewareNotFoundError: function () {
            return b;
          },
          MissingStaticPage: function () {
            return E;
          },
          NormalizeError: function () {
            return d;
          },
          PageNotFoundError: function () {
            return g;
          },
          SP: function () {
            return f;
          },
          ST: function () {
            return m;
          },
          WEB_VITALS: function () {
            return r;
          },
          execOnce: function () {
            return n;
          },
          getDisplayName: function () {
            return l;
          },
          getLocationOrigin: function () {
            return s;
          },
          getURL: function () {
            return a;
          },
          isAbsoluteUrl: function () {
            return o;
          },
          isResSent: function () {
            return u;
          },
          loadGetInitialProps: function () {
            return c;
          },
          normalizeRepeatedSlashes: function () {
            return h;
          },
          stringifyError: function () {
            return y;
          },
        }));
      let r = ["CLS", "FCP", "FID", "INP", "LCP", "TTFB"];
      function n(e) {
        let t,
          r = !1;
        return function () {
          for (var n = arguments.length, i = Array(n), o = 0; o < n; o++)
            i[o] = arguments[o];
          return (r || ((r = !0), (t = e(...i))), t);
        };
      }
      let i = /^[a-zA-Z][a-zA-Z\d+\-.]*?:/,
        o = (e) => i.test(e);
      function s() {
        let { protocol: e, hostname: t, port: r } = window.location;
        return e + "//" + t + (r ? ":" + r : "");
      }
      function a() {
        let { href: e } = window.location,
          t = s();
        return e.substring(t.length);
      }
      function l(e) {
        return "string" == typeof e ? e : e.displayName || e.name || "Unknown";
      }
      function u(e) {
        return e.finished || e.headersSent;
      }
      function h(e) {
        let t = e.split("?");
        return (
          t[0].replace(/\\/g, "/").replace(/\/\/+/g, "/") +
          (t[1] ? "?" + t.slice(1).join("?") : "")
        );
      }
      async function c(e, t) {
        let r = t.res || (t.ctx && t.ctx.res);
        if (!e.getInitialProps)
          return t.ctx && t.Component
            ? { pageProps: await c(t.Component, t.ctx) }
            : {};
        let n = await e.getInitialProps(t);
        if (r && u(r)) return n;
        if (!n)
          throw Error(
            '"' +
              l(e) +
              '.getInitialProps()" should resolve to an object. But found "' +
              n +
              '" instead.',
          );
        return n;
      }
      let f = "undefined" != typeof performance,
        m =
          f &&
          ["mark", "measure", "getEntriesByName"].every(
            (e) => "function" == typeof performance[e],
          );
      class p extends Error {}
      class d extends Error {}
      class g extends Error {
        constructor(e) {
          (super(),
            (this.code = "ENOENT"),
            (this.name = "PageNotFoundError"),
            (this.message = "Cannot find module for page: " + e));
        }
      }
      class E extends Error {
        constructor(e, t) {
          (super(),
            (this.message =
              "Failed to load static file for page: " + e + " " + t));
        }
      }
      class b extends Error {
        constructor() {
          (super(),
            (this.code = "ENOENT"),
            (this.message = "Cannot find the middleware module"));
        }
      }
      function y(e) {
        return JSON.stringify({ message: e.message, stack: e.stack });
      }
    },
    3879: function (e, t, r) {
      r.d(t, {
        default: function () {
          return u;
        },
      });
      var n = r(231),
        i = r.n(n),
        o = r(6463),
        s = r(2265),
        a = r(2756),
        l = r(7437),
        u = (0, s.forwardRef)(function (e, t) {
          let {
              href: r,
              locale: n,
              localeCookie: s,
              onClick: u,
              prefetch: h,
              ...c
            } = e,
            f = (0, a.bU)(),
            m = null != n && n !== f,
            p = (0, o.usePathname)();
          return (
            m && (h = !1),
            (0, l.jsx)(i(), {
              ref: t,
              href: r,
              hrefLang: m ? n : void 0,
              onClick: function (e) {
                ((function (e, t, r, n) {
                  if (!e || !(n !== r && null != n) || !t) return;
                  let i = (function (e, t = window.location.pathname) {
                      return "/" === e ? t : t.replace(e, "");
                    })(t),
                    { name: o, ...s } = e;
                  s.path || (s.path = "" !== i ? i : "/");
                  let a = `${o}=${n};`;
                  for (let [e, t] of Object.entries(s))
                    ((a += `${"maxAge" === e ? "max-age" : e}`),
                      "boolean" != typeof t && (a += "=" + t),
                      (a += ";"));
                  document.cookie = a;
                })(s, p, f, n),
                  u && u(e));
              },
              prefetch: h,
              ...c,
            })
          );
        });
    },
    2756: function (e, t, r) {
      r.d(t, {
        Pj: function () {
          return e_;
        },
        Gb: function () {
          return eB;
        },
        bU: function () {
          return eN;
        },
        T_: function () {
          return eA;
        },
      });
      var n,
        i,
        o,
        s,
        a,
        l,
        u = r(2265);
      function h(e, t) {
        let r = t && t.cache ? t.cache : d,
          n = t && t.serializer ? t.serializer : m;
        return (
          t && t.strategy
            ? t.strategy
            : function (e, t) {
                var r, n;
                let i = 1 === e.length ? c : f;
                return (
                  (r = t.cache.create()),
                  (n = t.serializer),
                  i.bind(this, e, r, n)
                );
              }
        )(e, { cache: r, serializer: n });
      }
      function c(e, t, r, n) {
        let i =
            null == n || "number" == typeof n || "boolean" == typeof n
              ? n
              : r(n),
          o = t.get(i);
        return (void 0 === o && ((o = e.call(this, n)), t.set(i, o)), o);
      }
      function f(e, t, r) {
        let n = Array.prototype.slice.call(arguments, 3),
          i = r(n),
          o = t.get(i);
        return (void 0 === o && ((o = e.apply(this, n)), t.set(i, o)), o);
      }
      let m = function () {
        return JSON.stringify(arguments);
      };
      class p {
        cache;
        constructor() {
          this.cache = Object.create(null);
        }
        get(e) {
          return this.cache[e];
        }
        set(e, t) {
          this.cache[e] = t;
        }
      }
      let d = {
          create: function () {
            return new p();
          },
        },
        g = {
          variadic: function (e, t) {
            var r, n;
            return (
              (r = t.cache.create()),
              (n = t.serializer),
              f.bind(this, e, r, n)
            );
          },
          monadic: function (e, t) {
            var r, n;
            return (
              (r = t.cache.create()),
              (n = t.serializer),
              c.bind(this, e, r, n)
            );
          },
        };
      class E extends Error {
        constructor(e, t) {
          let r = e;
          (t && (r += ": " + t),
            super(r),
            (this.code = e),
            t && (this.originalMessage = t));
        }
      }
      var b =
        (((n = b || {}).MISSING_MESSAGE = "MISSING_MESSAGE"),
        (n.MISSING_FORMAT = "MISSING_FORMAT"),
        (n.ENVIRONMENT_FALLBACK = "ENVIRONMENT_FALLBACK"),
        (n.INSUFFICIENT_PATH = "INSUFFICIENT_PATH"),
        (n.INVALID_MESSAGE = "INVALID_MESSAGE"),
        (n.INVALID_KEY = "INVALID_KEY"),
        (n.FORMATTING_ERROR = "FORMATTING_ERROR"),
        n);
      function y() {
        return {
          dateTime: {},
          number: {},
          message: {},
          relativeTime: {},
          pluralRules: {},
          list: {},
          displayNames: {},
        };
      }
      function T(e, t) {
        return h(e, {
          cache: {
            create: () => ({
              get: (e) => t[e],
              set(e, r) {
                t[e] = r;
              },
            }),
          },
          strategy: g.variadic,
        });
      }
      function _(e, t) {
        return T((...t) => new e(...t), t);
      }
      function H(e) {
        return {
          getDateTimeFormat: _(Intl.DateTimeFormat, e.dateTime),
          getNumberFormat: _(Intl.NumberFormat, e.number),
          getPluralRules: _(Intl.PluralRules, e.pluralRules),
          getRelativeTimeFormat: _(Intl.RelativeTimeFormat, e.relativeTime),
          getListFormat: _(Intl.ListFormat, e.list),
          getDisplayNames: _(Intl.DisplayNames, e.displayNames),
        };
      }
      let P =
          (((i = {})[(i.literal = 0)] = "literal"),
          (i[(i.argument = 1)] = "argument"),
          (i[(i.number = 2)] = "number"),
          (i[(i.date = 3)] = "date"),
          (i[(i.time = 4)] = "time"),
          (i[(i.select = 5)] = "select"),
          (i[(i.plural = 6)] = "plural"),
          (i[(i.pound = 7)] = "pound"),
          (i[(i.tag = 8)] = "tag"),
          i),
        S =
          (((o = {})[(o.number = 0)] = "number"),
          (o[(o.dateTime = 1)] = "dateTime"),
          o);
      function A(e) {
        return e.type === P.literal;
      }
      function N(e) {
        return e.type === P.number;
      }
      function B(e) {
        return e.type === P.date;
      }
      function R(e) {
        return e.type === P.time;
      }
      function I(e) {
        return e.type === P.select;
      }
      function M(e) {
        return e.type === P.plural;
      }
      function L(e) {
        return e.type === P.tag;
      }
      function O(e) {
        return !!(e && "object" == typeof e && e.type === S.number);
      }
      function v(e) {
        return !!(e && "object" == typeof e && e.type === S.dateTime);
      }
      let C =
          (((s = {})[(s.EXPECT_ARGUMENT_CLOSING_BRACE = 1)] =
            "EXPECT_ARGUMENT_CLOSING_BRACE"),
          (s[(s.EMPTY_ARGUMENT = 2)] = "EMPTY_ARGUMENT"),
          (s[(s.MALFORMED_ARGUMENT = 3)] = "MALFORMED_ARGUMENT"),
          (s[(s.EXPECT_ARGUMENT_TYPE = 4)] = "EXPECT_ARGUMENT_TYPE"),
          (s[(s.INVALID_ARGUMENT_TYPE = 5)] = "INVALID_ARGUMENT_TYPE"),
          (s[(s.EXPECT_ARGUMENT_STYLE = 6)] = "EXPECT_ARGUMENT_STYLE"),
          (s[(s.INVALID_NUMBER_SKELETON = 7)] = "INVALID_NUMBER_SKELETON"),
          (s[(s.INVALID_DATE_TIME_SKELETON = 8)] =
            "INVALID_DATE_TIME_SKELETON"),
          (s[(s.EXPECT_NUMBER_SKELETON = 9)] = "EXPECT_NUMBER_SKELETON"),
          (s[(s.EXPECT_DATE_TIME_SKELETON = 10)] = "EXPECT_DATE_TIME_SKELETON"),
          (s[(s.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE = 11)] =
            "UNCLOSED_QUOTE_IN_ARGUMENT_STYLE"),
          (s[(s.EXPECT_SELECT_ARGUMENT_OPTIONS = 12)] =
            "EXPECT_SELECT_ARGUMENT_OPTIONS"),
          (s[(s.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE = 13)] =
            "EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE"),
          (s[(s.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE = 14)] =
            "INVALID_PLURAL_ARGUMENT_OFFSET_VALUE"),
          (s[(s.EXPECT_SELECT_ARGUMENT_SELECTOR = 15)] =
            "EXPECT_SELECT_ARGUMENT_SELECTOR"),
          (s[(s.EXPECT_PLURAL_ARGUMENT_SELECTOR = 16)] =
            "EXPECT_PLURAL_ARGUMENT_SELECTOR"),
          (s[(s.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT = 17)] =
            "EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT"),
          (s[(s.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT = 18)] =
            "EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT"),
          (s[(s.INVALID_PLURAL_ARGUMENT_SELECTOR = 19)] =
            "INVALID_PLURAL_ARGUMENT_SELECTOR"),
          (s[(s.DUPLICATE_PLURAL_ARGUMENT_SELECTOR = 20)] =
            "DUPLICATE_PLURAL_ARGUMENT_SELECTOR"),
          (s[(s.DUPLICATE_SELECT_ARGUMENT_SELECTOR = 21)] =
            "DUPLICATE_SELECT_ARGUMENT_SELECTOR"),
          (s[(s.MISSING_OTHER_CLAUSE = 22)] = "MISSING_OTHER_CLAUSE"),
          (s[(s.INVALID_TAG = 23)] = "INVALID_TAG"),
          (s[(s.INVALID_TAG_NAME = 25)] = "INVALID_TAG_NAME"),
          (s[(s.UNMATCHED_CLOSING_TAG = 26)] = "UNMATCHED_CLOSING_TAG"),
          (s[(s.UNCLOSED_TAG = 27)] = "UNCLOSED_TAG"),
          s),
        w = /[    -   　]/,
        U =
          /(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g,
        G = /[\t-\r ‎‏  ]/i,
        D = /^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g,
        F = /^(@+)?(\+|#+)?[rs]?$/g,
        k = /(\*)(0+)|(#+)(0+)|(0+)/g,
        j = /^(0+)$/;
      function x(e) {
        let t = {};
        return (
          "r" === e[e.length - 1]
            ? (t.roundingPriority = "morePrecision")
            : "s" === e[e.length - 1] && (t.roundingPriority = "lessPrecision"),
          e.replace(F, function (e, r, n) {
            return (
              "string" != typeof n
                ? ((t.minimumSignificantDigits = r.length),
                  (t.maximumSignificantDigits = r.length))
                : "+" === n
                  ? (t.minimumSignificantDigits = r.length)
                  : "#" === r[0]
                    ? (t.maximumSignificantDigits = r.length)
                    : ((t.minimumSignificantDigits = r.length),
                      (t.maximumSignificantDigits =
                        r.length + ("string" == typeof n ? n.length : 0))),
              ""
            );
          }),
          t
        );
      }
      function V(e) {
        switch (e) {
          case "sign-auto":
            return { signDisplay: "auto" };
          case "sign-accounting":
          case "()":
            return { currencySign: "accounting" };
          case "sign-always":
          case "+!":
            return { signDisplay: "always" };
          case "sign-accounting-always":
          case "()!":
            return { signDisplay: "always", currencySign: "accounting" };
          case "sign-except-zero":
          case "+?":
            return { signDisplay: "exceptZero" };
          case "sign-accounting-except-zero":
          case "()?":
            return { signDisplay: "exceptZero", currencySign: "accounting" };
          case "sign-never":
          case "+_":
            return { signDisplay: "never" };
        }
      }
      function K(e) {
        return V(e) || {};
      }
      let X = {
          "001": ["H", "h"],
          419: ["h", "H", "hB", "hb"],
          AC: ["H", "h", "hb", "hB"],
          AD: ["H", "hB"],
          AE: ["h", "hB", "hb", "H"],
          AF: ["H", "hb", "hB", "h"],
          AG: ["h", "hb", "H", "hB"],
          AI: ["H", "h", "hb", "hB"],
          AL: ["h", "H", "hB"],
          AM: ["H", "hB"],
          AO: ["H", "hB"],
          AR: ["h", "H", "hB", "hb"],
          AS: ["h", "H"],
          AT: ["H", "hB"],
          AU: ["h", "hb", "H", "hB"],
          AW: ["H", "hB"],
          AX: ["H"],
          AZ: ["H", "hB", "h"],
          BA: ["H", "hB", "h"],
          BB: ["h", "hb", "H", "hB"],
          BD: ["h", "hB", "H"],
          BE: ["H", "hB"],
          BF: ["H", "hB"],
          BG: ["H", "hB", "h"],
          BH: ["h", "hB", "hb", "H"],
          BI: ["H", "h"],
          BJ: ["H", "hB"],
          BL: ["H", "hB"],
          BM: ["h", "hb", "H", "hB"],
          BN: ["hb", "hB", "h", "H"],
          BO: ["h", "H", "hB", "hb"],
          BQ: ["H"],
          BR: ["H", "hB"],
          BS: ["h", "hb", "H", "hB"],
          BT: ["h", "H"],
          BW: ["H", "h", "hb", "hB"],
          BY: ["H", "h"],
          BZ: ["H", "h", "hb", "hB"],
          CA: ["h", "hb", "H", "hB"],
          CC: ["H", "h", "hb", "hB"],
          CD: ["hB", "H"],
          CF: ["H", "h", "hB"],
          CG: ["H", "hB"],
          CH: ["H", "hB", "h"],
          CI: ["H", "hB"],
          CK: ["H", "h", "hb", "hB"],
          CL: ["h", "H", "hB", "hb"],
          CM: ["H", "h", "hB"],
          CN: ["H", "hB", "hb", "h"],
          CO: ["h", "H", "hB", "hb"],
          CP: ["H"],
          CR: ["h", "H", "hB", "hb"],
          CU: ["h", "H", "hB", "hb"],
          CV: ["H", "hB"],
          CW: ["H", "hB"],
          CX: ["H", "h", "hb", "hB"],
          CY: ["h", "H", "hb", "hB"],
          CZ: ["H"],
          DE: ["H", "hB"],
          DG: ["H", "h", "hb", "hB"],
          DJ: ["h", "H"],
          DK: ["H"],
          DM: ["h", "hb", "H", "hB"],
          DO: ["h", "H", "hB", "hb"],
          DZ: ["h", "hB", "hb", "H"],
          EA: ["H", "h", "hB", "hb"],
          EC: ["h", "H", "hB", "hb"],
          EE: ["H", "hB"],
          EG: ["h", "hB", "hb", "H"],
          EH: ["h", "hB", "hb", "H"],
          ER: ["h", "H"],
          ES: ["H", "hB", "h", "hb"],
          ET: ["hB", "hb", "h", "H"],
          FI: ["H"],
          FJ: ["h", "hb", "H", "hB"],
          FK: ["H", "h", "hb", "hB"],
          FM: ["h", "hb", "H", "hB"],
          FO: ["H", "h"],
          FR: ["H", "hB"],
          GA: ["H", "hB"],
          GB: ["H", "h", "hb", "hB"],
          GD: ["h", "hb", "H", "hB"],
          GE: ["H", "hB", "h"],
          GF: ["H", "hB"],
          GG: ["H", "h", "hb", "hB"],
          GH: ["h", "H"],
          GI: ["H", "h", "hb", "hB"],
          GL: ["H", "h"],
          GM: ["h", "hb", "H", "hB"],
          GN: ["H", "hB"],
          GP: ["H", "hB"],
          GQ: ["H", "hB", "h", "hb"],
          GR: ["h", "H", "hb", "hB"],
          GS: ["H", "h", "hb", "hB"],
          GT: ["h", "H", "hB", "hb"],
          GU: ["h", "hb", "H", "hB"],
          GW: ["H", "hB"],
          GY: ["h", "hb", "H", "hB"],
          HK: ["h", "hB", "hb", "H"],
          HN: ["h", "H", "hB", "hb"],
          HR: ["H", "hB"],
          HU: ["H", "h"],
          IC: ["H", "h", "hB", "hb"],
          ID: ["H"],
          IE: ["H", "h", "hb", "hB"],
          IL: ["H", "hB"],
          IM: ["H", "h", "hb", "hB"],
          IN: ["h", "H"],
          IO: ["H", "h", "hb", "hB"],
          IQ: ["h", "hB", "hb", "H"],
          IR: ["hB", "H"],
          IS: ["H"],
          IT: ["H", "hB"],
          JE: ["H", "h", "hb", "hB"],
          JM: ["h", "hb", "H", "hB"],
          JO: ["h", "hB", "hb", "H"],
          JP: ["H", "K", "h"],
          KE: ["hB", "hb", "H", "h"],
          KG: ["H", "h", "hB", "hb"],
          KH: ["hB", "h", "H", "hb"],
          KI: ["h", "hb", "H", "hB"],
          KM: ["H", "h", "hB", "hb"],
          KN: ["h", "hb", "H", "hB"],
          KP: ["h", "H", "hB", "hb"],
          KR: ["h", "H", "hB", "hb"],
          KW: ["h", "hB", "hb", "H"],
          KY: ["h", "hb", "H", "hB"],
          KZ: ["H", "hB"],
          LA: ["H", "hb", "hB", "h"],
          LB: ["h", "hB", "hb", "H"],
          LC: ["h", "hb", "H", "hB"],
          LI: ["H", "hB", "h"],
          LK: ["H", "h", "hB", "hb"],
          LR: ["h", "hb", "H", "hB"],
          LS: ["h", "H"],
          LT: ["H", "h", "hb", "hB"],
          LU: ["H", "h", "hB"],
          LV: ["H", "hB", "hb", "h"],
          LY: ["h", "hB", "hb", "H"],
          MA: ["H", "h", "hB", "hb"],
          MC: ["H", "hB"],
          MD: ["H", "hB"],
          ME: ["H", "hB", "h"],
          MF: ["H", "hB"],
          MG: ["H", "h"],
          MH: ["h", "hb", "H", "hB"],
          MK: ["H", "h", "hb", "hB"],
          ML: ["H"],
          MM: ["hB", "hb", "H", "h"],
          MN: ["H", "h", "hb", "hB"],
          MO: ["h", "hB", "hb", "H"],
          MP: ["h", "hb", "H", "hB"],
          MQ: ["H", "hB"],
          MR: ["h", "hB", "hb", "H"],
          MS: ["H", "h", "hb", "hB"],
          MT: ["H", "h"],
          MU: ["H", "h"],
          MV: ["H", "h"],
          MW: ["h", "hb", "H", "hB"],
          MX: ["h", "H", "hB", "hb"],
          MY: ["hb", "hB", "h", "H"],
          MZ: ["H", "hB"],
          NA: ["h", "H", "hB", "hb"],
          NC: ["H", "hB"],
          NE: ["H"],
          NF: ["H", "h", "hb", "hB"],
          NG: ["H", "h", "hb", "hB"],
          NI: ["h", "H", "hB", "hb"],
          NL: ["H", "hB"],
          NO: ["H", "h"],
          NP: ["H", "h", "hB"],
          NR: ["H", "h", "hb", "hB"],
          NU: ["H", "h", "hb", "hB"],
          NZ: ["h", "hb", "H", "hB"],
          OM: ["h", "hB", "hb", "H"],
          PA: ["h", "H", "hB", "hb"],
          PE: ["h", "H", "hB", "hb"],
          PF: ["H", "h", "hB"],
          PG: ["h", "H"],
          PH: ["h", "hB", "hb", "H"],
          PK: ["h", "hB", "H"],
          PL: ["H", "h"],
          PM: ["H", "hB"],
          PN: ["H", "h", "hb", "hB"],
          PR: ["h", "H", "hB", "hb"],
          PS: ["h", "hB", "hb", "H"],
          PT: ["H", "hB"],
          PW: ["h", "H"],
          PY: ["h", "H", "hB", "hb"],
          QA: ["h", "hB", "hb", "H"],
          RE: ["H", "hB"],
          RO: ["H", "hB"],
          RS: ["H", "hB", "h"],
          RU: ["H"],
          RW: ["H", "h"],
          SA: ["h", "hB", "hb", "H"],
          SB: ["h", "hb", "H", "hB"],
          SC: ["H", "h", "hB"],
          SD: ["h", "hB", "hb", "H"],
          SE: ["H"],
          SG: ["h", "hb", "H", "hB"],
          SH: ["H", "h", "hb", "hB"],
          SI: ["H", "hB"],
          SJ: ["H"],
          SK: ["H"],
          SL: ["h", "hb", "H", "hB"],
          SM: ["H", "h", "hB"],
          SN: ["H", "h", "hB"],
          SO: ["h", "H"],
          SR: ["H", "hB"],
          SS: ["h", "hb", "H", "hB"],
          ST: ["H", "hB"],
          SV: ["h", "H", "hB", "hb"],
          SX: ["H", "h", "hb", "hB"],
          SY: ["h", "hB", "hb", "H"],
          SZ: ["h", "hb", "H", "hB"],
          TA: ["H", "h", "hb", "hB"],
          TC: ["h", "hb", "H", "hB"],
          TD: ["h", "H", "hB"],
          TF: ["H", "h", "hB"],
          TG: ["H", "hB"],
          TH: ["H", "h"],
          TJ: ["H", "h"],
          TL: ["H", "hB", "hb", "h"],
          TM: ["H", "h"],
          TN: ["h", "hB", "hb", "H"],
          TO: ["h", "H"],
          TR: ["H", "hB"],
          TT: ["h", "hb", "H", "hB"],
          TW: ["hB", "hb", "h", "H"],
          TZ: ["hB", "hb", "H", "h"],
          UA: ["H", "hB", "h"],
          UG: ["hB", "hb", "H", "h"],
          UM: ["h", "hb", "H", "hB"],
          US: ["h", "hb", "H", "hB"],
          UY: ["h", "H", "hB", "hb"],
          UZ: ["H", "hB", "h"],
          VA: ["H", "h", "hB"],
          VC: ["h", "hb", "H", "hB"],
          VE: ["h", "H", "hB", "hb"],
          VG: ["h", "hb", "H", "hB"],
          VI: ["h", "hb", "H", "hB"],
          VN: ["H", "h"],
          VU: ["h", "H"],
          WF: ["H", "hB"],
          WS: ["h", "H"],
          XK: ["H", "hB", "h"],
          YE: ["h", "hB", "hb", "H"],
          YT: ["H", "hB"],
          ZA: ["H", "h", "hb", "hB"],
          ZM: ["h", "hb", "H", "hB"],
          ZW: ["H", "h"],
          "af-ZA": ["H", "h", "hB", "hb"],
          "ar-001": ["h", "hB", "hb", "H"],
          "ca-ES": ["H", "h", "hB"],
          "en-001": ["h", "hb", "H", "hB"],
          "en-HK": ["h", "hb", "H", "hB"],
          "en-IL": ["H", "h", "hb", "hB"],
          "en-MY": ["h", "hb", "H", "hB"],
          "es-BR": ["H", "h", "hB", "hb"],
          "es-ES": ["H", "h", "hB", "hb"],
          "es-GQ": ["H", "h", "hB", "hb"],
          "fr-CA": ["H", "h", "hB"],
          "gl-ES": ["H", "h", "hB"],
          "gu-IN": ["hB", "hb", "h", "H"],
          "hi-IN": ["hB", "h", "H"],
          "it-CH": ["H", "h", "hB"],
          "it-IT": ["H", "h", "hB"],
          "kn-IN": ["hB", "h", "H"],
          "ku-SY": ["H", "hB"],
          "ml-IN": ["hB", "h", "H"],
          "mr-IN": ["hB", "hb", "h", "H"],
          "pa-IN": ["hB", "hb", "h", "H"],
          "ta-IN": ["hB", "h", "hb", "H"],
          "te-IN": ["hB", "h", "H"],
          "zu-ZA": ["H", "hB", "hb", "h"],
        },
        Z = RegExp(`^${w.source}*`),
        W = RegExp(`${w.source}*$`);
      function Y(e, t) {
        return { start: e, end: t };
      }
      let $ = !!Object.fromEntries,
        z = !!String.prototype.trimStart,
        q = !!String.prototype.trimEnd,
        Q = $
          ? Object.fromEntries
          : function (e) {
              let t = {};
              for (let [r, n] of e) t[r] = n;
              return t;
            },
        J = z
          ? function (e) {
              return e.trimStart();
            }
          : function (e) {
              return e.replace(Z, "");
            },
        ee = q
          ? function (e) {
              return e.trimEnd();
            }
          : function (e) {
              return e.replace(W, "");
            },
        et = RegExp("([^\\p{White_Space}\\p{Pattern_Syntax}]*)", "yu");
      class er {
        message;
        position;
        locale;
        ignoreTag;
        requiresOtherClause;
        shouldParseSkeletons;
        constructor(e, t = {}) {
          ((this.message = e),
            (this.position = { offset: 0, line: 1, column: 1 }),
            (this.ignoreTag = !!t.ignoreTag),
            (this.locale = t.locale),
            (this.requiresOtherClause = !!t.requiresOtherClause),
            (this.shouldParseSkeletons = !!t.shouldParseSkeletons));
        }
        parse() {
          if (0 !== this.offset()) throw Error("parser can only be used once");
          return this.parseMessage(0, "", !1);
        }
        parseMessage(e, t, r) {
          let n = [];
          for (; !this.isEOF(); ) {
            let i = this.char();
            if (123 === i) {
              let t = this.parseArgument(e, r);
              if (t.err) return t;
              n.push(t.val);
            } else if (125 === i && e > 0) break;
            else if (35 === i && ("plural" === t || "selectordinal" === t)) {
              let e = this.clonePosition();
              (this.bump(),
                n.push({
                  type: P.pound,
                  location: Y(e, this.clonePosition()),
                }));
            } else if (60 !== i || this.ignoreTag || 47 !== this.peek()) {
              if (60 === i && !this.ignoreTag && en(this.peek() || 0)) {
                let r = this.parseTag(e, t);
                if (r.err) return r;
                n.push(r.val);
              } else {
                let r = this.parseLiteral(e, t);
                if (r.err) return r;
                n.push(r.val);
              }
            } else {
              if (!r)
                return this.error(
                  C.UNMATCHED_CLOSING_TAG,
                  Y(this.clonePosition(), this.clonePosition()),
                );
              break;
            }
          }
          return { val: n, err: null };
        }
        parseTag(e, t) {
          let r = this.clonePosition();
          this.bump();
          let n = this.parseTagName();
          if ((this.bumpSpace(), this.bumpIf("/>")))
            return {
              val: {
                type: P.literal,
                value: `<${n}/>`,
                location: Y(r, this.clonePosition()),
              },
              err: null,
            };
          if (!this.bumpIf(">"))
            return this.error(C.INVALID_TAG, Y(r, this.clonePosition()));
          {
            let i = this.parseMessage(e + 1, t, !0);
            if (i.err) return i;
            let o = i.val,
              s = this.clonePosition();
            if (!this.bumpIf("</"))
              return this.error(C.UNCLOSED_TAG, Y(r, this.clonePosition()));
            {
              if (this.isEOF() || !en(this.char()))
                return this.error(C.INVALID_TAG, Y(s, this.clonePosition()));
              let e = this.clonePosition();
              return n !== this.parseTagName()
                ? this.error(
                    C.UNMATCHED_CLOSING_TAG,
                    Y(e, this.clonePosition()),
                  )
                : (this.bumpSpace(), this.bumpIf(">"))
                  ? {
                      val: {
                        type: P.tag,
                        value: n,
                        children: o,
                        location: Y(r, this.clonePosition()),
                      },
                      err: null,
                    }
                  : this.error(C.INVALID_TAG, Y(s, this.clonePosition()));
            }
          }
        }
        parseTagName() {
          var e;
          let t = this.offset();
          for (
            this.bump();
            !this.isEOF() &&
            (45 === (e = this.char()) ||
              46 === e ||
              (e >= 48 && e <= 57) ||
              95 === e ||
              (e >= 97 && e <= 122) ||
              (e >= 65 && e <= 90) ||
              183 == e ||
              (e >= 192 && e <= 214) ||
              (e >= 216 && e <= 246) ||
              (e >= 248 && e <= 893) ||
              (e >= 895 && e <= 8191) ||
              (e >= 8204 && e <= 8205) ||
              (e >= 8255 && e <= 8256) ||
              (e >= 8304 && e <= 8591) ||
              (e >= 11264 && e <= 12271) ||
              (e >= 12289 && e <= 55295) ||
              (e >= 63744 && e <= 64975) ||
              (e >= 65008 && e <= 65533) ||
              (e >= 65536 && e <= 983039));
          )
            this.bump();
          return this.message.slice(t, this.offset());
        }
        parseLiteral(e, t) {
          let r = this.clonePosition(),
            n = "";
          for (;;) {
            let r = this.tryParseQuote(t);
            if (r) {
              n += r;
              continue;
            }
            let i = this.tryParseUnquoted(e, t);
            if (i) {
              n += i;
              continue;
            }
            let o = this.tryParseLeftAngleBracket();
            if (o) {
              n += o;
              continue;
            }
            break;
          }
          let i = Y(r, this.clonePosition());
          return { val: { type: P.literal, value: n, location: i }, err: null };
        }
        tryParseLeftAngleBracket() {
          var e;
          return this.isEOF() ||
            60 !== this.char() ||
            (!this.ignoreTag && (en((e = this.peek() || 0)) || 47 === e))
            ? null
            : (this.bump(), "<");
        }
        tryParseQuote(e) {
          if (this.isEOF() || 39 !== this.char()) return null;
          switch (this.peek()) {
            case 39:
              return (this.bump(), this.bump(), "'");
            case 123:
            case 60:
            case 62:
            case 125:
              break;
            case 35:
              if ("plural" === e || "selectordinal" === e) break;
              return null;
            default:
              return null;
          }
          this.bump();
          let t = [this.char()];
          for (this.bump(); !this.isEOF(); ) {
            let e = this.char();
            if (39 === e) {
              if (39 === this.peek()) (t.push(39), this.bump());
              else {
                this.bump();
                break;
              }
            } else t.push(e);
            this.bump();
          }
          return String.fromCodePoint(...t);
        }
        tryParseUnquoted(e, t) {
          if (this.isEOF()) return null;
          let r = this.char();
          return 60 === r ||
            123 === r ||
            (35 === r && ("plural" === t || "selectordinal" === t)) ||
            (125 === r && e > 0)
            ? null
            : (this.bump(), String.fromCodePoint(r));
        }
        parseArgument(e, t) {
          let r = this.clonePosition();
          if ((this.bump(), this.bumpSpace(), this.isEOF()))
            return this.error(
              C.EXPECT_ARGUMENT_CLOSING_BRACE,
              Y(r, this.clonePosition()),
            );
          if (125 === this.char())
            return (
              this.bump(),
              this.error(C.EMPTY_ARGUMENT, Y(r, this.clonePosition()))
            );
          let n = this.parseIdentifierIfPossible().value;
          if (!n)
            return this.error(C.MALFORMED_ARGUMENT, Y(r, this.clonePosition()));
          if ((this.bumpSpace(), this.isEOF()))
            return this.error(
              C.EXPECT_ARGUMENT_CLOSING_BRACE,
              Y(r, this.clonePosition()),
            );
          switch (this.char()) {
            case 125:
              return (
                this.bump(),
                {
                  val: {
                    type: P.argument,
                    value: n,
                    location: Y(r, this.clonePosition()),
                  },
                  err: null,
                }
              );
            case 44:
              if ((this.bump(), this.bumpSpace(), this.isEOF()))
                return this.error(
                  C.EXPECT_ARGUMENT_CLOSING_BRACE,
                  Y(r, this.clonePosition()),
                );
              return this.parseArgumentOptions(e, t, n, r);
            default:
              return this.error(
                C.MALFORMED_ARGUMENT,
                Y(r, this.clonePosition()),
              );
          }
        }
        parseIdentifierIfPossible() {
          var e;
          let t = this.clonePosition(),
            r = this.offset(),
            n = ((e = this.message), (et.lastIndex = r), et.exec(e)[1] ?? ""),
            i = r + n.length;
          return (
            this.bumpTo(i),
            { value: n, location: Y(t, this.clonePosition()) }
          );
        }
        parseArgumentOptions(e, t, r, n) {
          let i = this.clonePosition(),
            o = this.parseIdentifierIfPossible().value,
            s = this.clonePosition();
          switch (o) {
            case "":
              return this.error(C.EXPECT_ARGUMENT_TYPE, Y(i, s));
            case "number":
            case "date":
            case "time": {
              this.bumpSpace();
              let e = null;
              if (this.bumpIf(",")) {
                this.bumpSpace();
                let t = this.clonePosition(),
                  r = this.parseSimpleArgStyleIfPossible();
                if (r.err) return r;
                let n = ee(r.val);
                if (0 === n.length)
                  return this.error(
                    C.EXPECT_ARGUMENT_STYLE,
                    Y(this.clonePosition(), this.clonePosition()),
                  );
                e = { style: n, styleLocation: Y(t, this.clonePosition()) };
              }
              let t = this.tryParseArgumentClose(n);
              if (t.err) return t;
              let i = Y(n, this.clonePosition());
              if (e && e.style.startsWith("::")) {
                let t = J(e.style.slice(2));
                if ("number" === o) {
                  let n = this.parseNumberSkeletonFromString(
                    t,
                    e.styleLocation,
                  );
                  if (n.err) return n;
                  return {
                    val: {
                      type: P.number,
                      value: r,
                      location: i,
                      style: n.val,
                    },
                    err: null,
                  };
                }
                {
                  if (0 === t.length)
                    return this.error(C.EXPECT_DATE_TIME_SKELETON, i);
                  let n = t;
                  this.locale &&
                    (n = (function (e, t) {
                      let r = "";
                      for (let n = 0; n < e.length; n++) {
                        let i = e.charAt(n);
                        if ("j" === i) {
                          let o = 0;
                          for (; n + 1 < e.length && e.charAt(n + 1) === i; )
                            (o++, n++);
                          let s = 1 + (1 & o),
                            a = o < 2 ? 1 : 3 + (o >> 1),
                            l = (function (e) {
                              let t,
                                r = e.hourCycle;
                              if (
                                (void 0 === r &&
                                  e.hourCycles &&
                                  e.hourCycles.length &&
                                  (r = e.hourCycles[0]),
                                r)
                              )
                                switch (r) {
                                  case "h24":
                                    return "k";
                                  case "h23":
                                    return "H";
                                  case "h12":
                                    return "h";
                                  case "h11":
                                    return "K";
                                  default:
                                    throw Error("Invalid hourCycle");
                                }
                              let n = e.language;
                              return (
                                "root" !== n && (t = e.maximize().region),
                                (X[t || ""] ||
                                  X[n || ""] ||
                                  X[`${n}-001`] ||
                                  X["001"])[0]
                              );
                            })(t);
                          for (("H" == l || "k" == l) && (a = 0); a-- > 0; )
                            r += "a";
                          for (; s-- > 0; ) r = l + r;
                        } else "J" === i ? (r += "H") : (r += i);
                      }
                      return r;
                    })(t, this.locale));
                  let s = {
                    type: S.dateTime,
                    pattern: n,
                    location: e.styleLocation,
                    parsedOptions: this.shouldParseSkeletons
                      ? (function (e) {
                          let t = {};
                          return (
                            e.replace(U, (e) => {
                              let r = e.length;
                              switch (e[0]) {
                                case "G":
                                  t.era =
                                    4 === r
                                      ? "long"
                                      : 5 === r
                                        ? "narrow"
                                        : "short";
                                  break;
                                case "y":
                                  t.year = 2 === r ? "2-digit" : "numeric";
                                  break;
                                case "Y":
                                case "u":
                                case "U":
                                case "r":
                                  throw RangeError(
                                    "`Y/u/U/r` (year) patterns are not supported, use `y` instead",
                                  );
                                case "q":
                                case "Q":
                                  throw RangeError(
                                    "`q/Q` (quarter) patterns are not supported",
                                  );
                                case "M":
                                case "L":
                                  t.month = [
                                    "numeric",
                                    "2-digit",
                                    "short",
                                    "long",
                                    "narrow",
                                  ][r - 1];
                                  break;
                                case "w":
                                case "W":
                                  throw RangeError(
                                    "`w/W` (week) patterns are not supported",
                                  );
                                case "d":
                                  t.day = ["numeric", "2-digit"][r - 1];
                                  break;
                                case "D":
                                case "F":
                                case "g":
                                  throw RangeError(
                                    "`D/F/g` (day) patterns are not supported, use `d` instead",
                                  );
                                case "E":
                                  t.weekday =
                                    4 === r
                                      ? "long"
                                      : 5 === r
                                        ? "narrow"
                                        : "short";
                                  break;
                                case "e":
                                  if (r < 4)
                                    throw RangeError(
                                      "`e..eee` (weekday) patterns are not supported",
                                    );
                                  t.weekday = [
                                    "short",
                                    "long",
                                    "narrow",
                                    "short",
                                  ][r - 4];
                                  break;
                                case "c":
                                  if (r < 4)
                                    throw RangeError(
                                      "`c..ccc` (weekday) patterns are not supported",
                                    );
                                  t.weekday = [
                                    "short",
                                    "long",
                                    "narrow",
                                    "short",
                                  ][r - 4];
                                  break;
                                case "a":
                                  t.hour12 = !0;
                                  break;
                                case "b":
                                case "B":
                                  throw RangeError(
                                    "`b/B` (period) patterns are not supported, use `a` instead",
                                  );
                                case "h":
                                  ((t.hourCycle = "h12"),
                                    (t.hour = ["numeric", "2-digit"][r - 1]));
                                  break;
                                case "H":
                                  ((t.hourCycle = "h23"),
                                    (t.hour = ["numeric", "2-digit"][r - 1]));
                                  break;
                                case "K":
                                  ((t.hourCycle = "h11"),
                                    (t.hour = ["numeric", "2-digit"][r - 1]));
                                  break;
                                case "k":
                                  ((t.hourCycle = "h24"),
                                    (t.hour = ["numeric", "2-digit"][r - 1]));
                                  break;
                                case "j":
                                case "J":
                                case "C":
                                  throw RangeError(
                                    "`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead",
                                  );
                                case "m":
                                  t.minute = ["numeric", "2-digit"][r - 1];
                                  break;
                                case "s":
                                  t.second = ["numeric", "2-digit"][r - 1];
                                  break;
                                case "S":
                                case "A":
                                  throw RangeError(
                                    "`S/A` (second) patterns are not supported, use `s` instead",
                                  );
                                case "z":
                                  t.timeZoneName = r < 4 ? "short" : "long";
                                  break;
                                case "Z":
                                case "O":
                                case "v":
                                case "V":
                                case "X":
                                case "x":
                                  throw RangeError(
                                    "`Z/O/v/V/X/x` (timeZone) patterns are not supported, use `z` instead",
                                  );
                              }
                              return "";
                            }),
                            t
                          );
                        })(n)
                      : {},
                  };
                  return {
                    val: {
                      type: "date" === o ? P.date : P.time,
                      value: r,
                      location: i,
                      style: s,
                    },
                    err: null,
                  };
                }
              }
              return {
                val: {
                  type:
                    "number" === o ? P.number : "date" === o ? P.date : P.time,
                  value: r,
                  location: i,
                  style: e?.style ?? null,
                },
                err: null,
              };
            }
            case "plural":
            case "selectordinal":
            case "select": {
              let i = this.clonePosition();
              if ((this.bumpSpace(), !this.bumpIf(",")))
                return this.error(
                  C.EXPECT_SELECT_ARGUMENT_OPTIONS,
                  Y(i, { ...i }),
                );
              this.bumpSpace();
              let s = this.parseIdentifierIfPossible(),
                a = 0;
              if ("select" !== o && "offset" === s.value) {
                if (!this.bumpIf(":"))
                  return this.error(
                    C.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE,
                    Y(this.clonePosition(), this.clonePosition()),
                  );
                this.bumpSpace();
                let e = this.tryParseDecimalInteger(
                  C.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE,
                  C.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE,
                );
                if (e.err) return e;
                (this.bumpSpace(),
                  (s = this.parseIdentifierIfPossible()),
                  (a = e.val));
              }
              let l = this.tryParsePluralOrSelectOptions(e, o, t, s);
              if (l.err) return l;
              let u = this.tryParseArgumentClose(n);
              if (u.err) return u;
              let h = Y(n, this.clonePosition());
              if ("select" === o)
                return {
                  val: {
                    type: P.select,
                    value: r,
                    options: Q(l.val),
                    location: h,
                  },
                  err: null,
                };
              return {
                val: {
                  type: P.plural,
                  value: r,
                  options: Q(l.val),
                  offset: a,
                  pluralType: "plural" === o ? "cardinal" : "ordinal",
                  location: h,
                },
                err: null,
              };
            }
            default:
              return this.error(C.INVALID_ARGUMENT_TYPE, Y(i, s));
          }
        }
        tryParseArgumentClose(e) {
          return this.isEOF() || 125 !== this.char()
            ? this.error(
                C.EXPECT_ARGUMENT_CLOSING_BRACE,
                Y(e, this.clonePosition()),
              )
            : (this.bump(), { val: !0, err: null });
        }
        parseSimpleArgStyleIfPossible() {
          let e = 0,
            t = this.clonePosition();
          for (; !this.isEOF(); )
            switch (this.char()) {
              case 39: {
                this.bump();
                let e = this.clonePosition();
                if (!this.bumpUntil("'"))
                  return this.error(
                    C.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE,
                    Y(e, this.clonePosition()),
                  );
                this.bump();
                break;
              }
              case 123:
                ((e += 1), this.bump());
                break;
              case 125:
                if (!(e > 0))
                  return {
                    val: this.message.slice(t.offset, this.offset()),
                    err: null,
                  };
                e -= 1;
                break;
              default:
                this.bump();
            }
          return {
            val: this.message.slice(t.offset, this.offset()),
            err: null,
          };
        }
        parseNumberSkeletonFromString(e, t) {
          let r = [];
          try {
            r = (function (e) {
              if (0 === e.length)
                throw Error("Number skeleton cannot be empty");
              let t = e.split(G).filter((e) => e.length > 0),
                r = [];
              for (let e of t) {
                let t = e.split("/");
                if (0 === t.length) throw Error("Invalid number skeleton");
                let [n, ...i] = t;
                for (let e of i)
                  if (0 === e.length) throw Error("Invalid number skeleton");
                r.push({ stem: n, options: i });
              }
              return r;
            })(e);
          } catch {
            return this.error(C.INVALID_NUMBER_SKELETON, t);
          }
          return {
            val: {
              type: S.number,
              tokens: r,
              location: t,
              parsedOptions: this.shouldParseSkeletons
                ? (function (e) {
                    let t = {};
                    for (let r of e) {
                      switch (r.stem) {
                        case "percent":
                        case "%":
                          t.style = "percent";
                          continue;
                        case "%x100":
                          ((t.style = "percent"), (t.scale = 100));
                          continue;
                        case "currency":
                          ((t.style = "currency"), (t.currency = r.options[0]));
                          continue;
                        case "group-off":
                        case ",_":
                          t.useGrouping = !1;
                          continue;
                        case "precision-integer":
                        case ".":
                          t.maximumFractionDigits = 0;
                          continue;
                        case "measure-unit":
                        case "unit":
                          ((t.style = "unit"),
                            (t.unit = r.options[0].replace(/^(.*?)-/, "")));
                          continue;
                        case "compact-short":
                        case "K":
                          ((t.notation = "compact"),
                            (t.compactDisplay = "short"));
                          continue;
                        case "compact-long":
                        case "KK":
                          ((t.notation = "compact"),
                            (t.compactDisplay = "long"));
                          continue;
                        case "scientific":
                          t = {
                            ...t,
                            notation: "scientific",
                            ...r.options.reduce(
                              (e, t) => ({ ...e, ...(V(t) || {}) }),
                              {},
                            ),
                          };
                          continue;
                        case "engineering":
                          t = {
                            ...t,
                            notation: "engineering",
                            ...r.options.reduce(
                              (e, t) => ({ ...e, ...(V(t) || {}) }),
                              {},
                            ),
                          };
                          continue;
                        case "notation-simple":
                          t.notation = "standard";
                          continue;
                        case "unit-width-narrow":
                          ((t.currencyDisplay = "narrowSymbol"),
                            (t.unitDisplay = "narrow"));
                          continue;
                        case "unit-width-short":
                          ((t.currencyDisplay = "code"),
                            (t.unitDisplay = "short"));
                          continue;
                        case "unit-width-full-name":
                          ((t.currencyDisplay = "name"),
                            (t.unitDisplay = "long"));
                          continue;
                        case "unit-width-iso-code":
                          t.currencyDisplay = "symbol";
                          continue;
                        case "scale":
                          t.scale = parseFloat(r.options[0]);
                          continue;
                        case "rounding-mode-floor":
                          t.roundingMode = "floor";
                          continue;
                        case "rounding-mode-ceiling":
                          t.roundingMode = "ceil";
                          continue;
                        case "rounding-mode-down":
                          t.roundingMode = "trunc";
                          continue;
                        case "rounding-mode-up":
                          t.roundingMode = "expand";
                          continue;
                        case "rounding-mode-half-even":
                          t.roundingMode = "halfEven";
                          continue;
                        case "rounding-mode-half-down":
                          t.roundingMode = "halfTrunc";
                          continue;
                        case "rounding-mode-half-up":
                          t.roundingMode = "halfExpand";
                          continue;
                        case "integer-width":
                          if (r.options.length > 1)
                            throw RangeError(
                              "integer-width stems only accept a single optional option",
                            );
                          r.options[0].replace(k, function (e, r, n, i, o, s) {
                            if (r) t.minimumIntegerDigits = n.length;
                            else if (i && o)
                              throw Error(
                                "We currently do not support maximum integer digits",
                              );
                            else if (s)
                              throw Error(
                                "We currently do not support exact integer digits",
                              );
                            return "";
                          });
                          continue;
                      }
                      if (j.test(r.stem)) {
                        t.minimumIntegerDigits = r.stem.length;
                        continue;
                      }
                      if (D.test(r.stem)) {
                        if (r.options.length > 1)
                          throw RangeError(
                            "Fraction-precision stems only accept a single optional option",
                          );
                        r.stem.replace(D, function (e, r, n, i, o, s) {
                          return (
                            "*" === n
                              ? (t.minimumFractionDigits = r.length)
                              : i && "#" === i[0]
                                ? (t.maximumFractionDigits = i.length)
                                : o && s
                                  ? ((t.minimumFractionDigits = o.length),
                                    (t.maximumFractionDigits =
                                      o.length + s.length))
                                  : ((t.minimumFractionDigits = r.length),
                                    (t.maximumFractionDigits = r.length)),
                            ""
                          );
                        });
                        let e = r.options[0];
                        "w" === e
                          ? (t = {
                              ...t,
                              trailingZeroDisplay: "stripIfInteger",
                            })
                          : e && (t = { ...t, ...x(e) });
                        continue;
                      }
                      if (F.test(r.stem)) {
                        t = { ...t, ...x(r.stem) };
                        continue;
                      }
                      let e = V(r.stem);
                      e && (t = { ...t, ...e });
                      let n = (function (e) {
                        let t;
                        if (
                          ("E" === e[0] && "E" === e[1]
                            ? ((t = { notation: "engineering" }),
                              (e = e.slice(2)))
                            : "E" === e[0] &&
                              ((t = { notation: "scientific" }),
                              (e = e.slice(1))),
                          t)
                        ) {
                          let r = e.slice(0, 2);
                          if (
                            ("+!" === r
                              ? ((t.signDisplay = "always"), (e = e.slice(2)))
                              : "+?" === r &&
                                ((t.signDisplay = "exceptZero"),
                                (e = e.slice(2))),
                            !j.test(e))
                          )
                            throw Error(
                              "Malformed concise eng/scientific notation",
                            );
                          t.minimumIntegerDigits = e.length;
                        }
                        return t;
                      })(r.stem);
                      n && (t = { ...t, ...n });
                    }
                    return t;
                  })(r)
                : {},
            },
            err: null,
          };
        }
        tryParsePluralOrSelectOptions(e, t, r, n) {
          let i = !1,
            o = [],
            s = new Set(),
            { value: a, location: l } = n;
          for (;;) {
            if (0 === a.length) {
              let e = this.clonePosition();
              if ("select" !== t && this.bumpIf("=")) {
                let t = this.tryParseDecimalInteger(
                  C.EXPECT_PLURAL_ARGUMENT_SELECTOR,
                  C.INVALID_PLURAL_ARGUMENT_SELECTOR,
                );
                if (t.err) return t;
                ((l = Y(e, this.clonePosition())),
                  (a = this.message.slice(e.offset, this.offset())));
              } else break;
            }
            if (s.has(a))
              return this.error(
                "select" === t
                  ? C.DUPLICATE_SELECT_ARGUMENT_SELECTOR
                  : C.DUPLICATE_PLURAL_ARGUMENT_SELECTOR,
                l,
              );
            ("other" === a && (i = !0), this.bumpSpace());
            let n = this.clonePosition();
            if (!this.bumpIf("{"))
              return this.error(
                "select" === t
                  ? C.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT
                  : C.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT,
                Y(this.clonePosition(), this.clonePosition()),
              );
            let u = this.parseMessage(e + 1, t, r);
            if (u.err) return u;
            let h = this.tryParseArgumentClose(n);
            if (h.err) return h;
            (o.push([
              a,
              { value: u.val, location: Y(n, this.clonePosition()) },
            ]),
              s.add(a),
              this.bumpSpace(),
              ({ value: a, location: l } = this.parseIdentifierIfPossible()));
          }
          return 0 === o.length
            ? this.error(
                "select" === t
                  ? C.EXPECT_SELECT_ARGUMENT_SELECTOR
                  : C.EXPECT_PLURAL_ARGUMENT_SELECTOR,
                Y(this.clonePosition(), this.clonePosition()),
              )
            : this.requiresOtherClause && !i
              ? this.error(
                  C.MISSING_OTHER_CLAUSE,
                  Y(this.clonePosition(), this.clonePosition()),
                )
              : { val: o, err: null };
        }
        tryParseDecimalInteger(e, t) {
          let r = 1,
            n = this.clonePosition();
          this.bumpIf("+") || (this.bumpIf("-") && (r = -1));
          let i = !1,
            o = 0;
          for (; !this.isEOF(); ) {
            let e = this.char();
            if (e >= 48 && e <= 57)
              ((i = !0), (o = 10 * o + (e - 48)), this.bump());
            else break;
          }
          let s = Y(n, this.clonePosition());
          return i
            ? Number.isSafeInteger((o *= r))
              ? { val: o, err: null }
              : this.error(t, s)
            : this.error(e, s);
        }
        offset() {
          return this.position.offset;
        }
        isEOF() {
          return this.offset() === this.message.length;
        }
        clonePosition() {
          return {
            offset: this.position.offset,
            line: this.position.line,
            column: this.position.column,
          };
        }
        char() {
          let e = this.position.offset;
          if (e >= this.message.length) throw Error("out of bound");
          let t = this.message.codePointAt(e);
          if (void 0 === t)
            throw Error(`Offset ${e} is at invalid UTF-16 code unit boundary`);
          return t;
        }
        error(e, t) {
          return {
            val: null,
            err: { kind: e, message: this.message, location: t },
          };
        }
        bump() {
          if (this.isEOF()) return;
          let e = this.char();
          10 === e
            ? ((this.position.line += 1),
              (this.position.column = 1),
              (this.position.offset += 1))
            : ((this.position.column += 1),
              (this.position.offset += e < 65536 ? 1 : 2));
        }
        bumpIf(e) {
          if (this.message.startsWith(e, this.offset())) {
            for (let t = 0; t < e.length; t++) this.bump();
            return !0;
          }
          return !1;
        }
        bumpUntil(e) {
          let t = this.offset(),
            r = this.message.indexOf(e, t);
          return r >= 0
            ? (this.bumpTo(r), !0)
            : (this.bumpTo(this.message.length), !1);
        }
        bumpTo(e) {
          if (this.offset() > e)
            throw Error(
              `targetOffset ${e} must be greater than or equal to the current offset ${this.offset()}`,
            );
          for (e = Math.min(e, this.message.length); ; ) {
            let t = this.offset();
            if (t === e) break;
            if (t > e)
              throw Error(
                `targetOffset ${e} is at invalid UTF-16 code unit boundary`,
              );
            if ((this.bump(), this.isEOF())) break;
          }
        }
        bumpSpace() {
          for (
            var e;
            !this.isEOF() &&
            (((e = this.char()) >= 9 && e <= 13) ||
              32 === e ||
              133 === e ||
              (e >= 8206 && e <= 8207) ||
              8232 === e ||
              8233 === e);
          )
            this.bump();
        }
        peek() {
          if (this.isEOF()) return null;
          let e = this.char(),
            t = this.offset();
          return this.message.charCodeAt(t + (e >= 65536 ? 2 : 1)) ?? null;
        }
      }
      function en(e) {
        return (e >= 97 && e <= 122) || (e >= 65 && e <= 90);
      }
      function ei(e, t = {}) {
        let r = new er(
          e,
          (t = { shouldParseSkeletons: !0, requiresOtherClause: !0, ...t }),
        ).parse();
        if (r.err) {
          let e = SyntaxError(C[r.err.kind]);
          throw (
            (e.location = r.err.location),
            (e.originalMessage = r.err.message),
            e
          );
        }
        return (
          t?.captureLocation ||
            (function e(t) {
              t.forEach((t) => {
                if ((delete t.location, I(t) || M(t)))
                  for (let r in t.options)
                    (delete t.options[r].location, e(t.options[r].value));
                else
                  N(t) && O(t.style)
                    ? delete t.style.location
                    : (B(t) || R(t)) && v(t.style)
                      ? delete t.style.location
                      : L(t) && e(t.children);
              });
            })(r.val),
          r.val
        );
      }
      let eo =
        (((a = {}).MISSING_VALUE = "MISSING_VALUE"),
        (a.INVALID_VALUE = "INVALID_VALUE"),
        (a.MISSING_INTL_API = "MISSING_INTL_API"),
        a);
      class es extends Error {
        code;
        originalMessage;
        constructor(e, t, r) {
          (super(e), (this.code = t), (this.originalMessage = r));
        }
        toString() {
          return `[formatjs Error: ${this.code}] ${this.message}`;
        }
      }
      class ea extends es {
        constructor(e, t, r, n) {
          super(
            `Invalid values for "${e}": "${t}". Options are "${Object.keys(r).join('", "')}"`,
            eo.INVALID_VALUE,
            n,
          );
        }
      }
      class el extends es {
        constructor(e, t, r) {
          super(`Value for "${e}" must be of type ${t}`, eo.INVALID_VALUE, r);
        }
      }
      class eu extends es {
        constructor(e, t) {
          super(
            `The intl string context variable "${e}" was not provided to the string "${t}"`,
            eo.MISSING_VALUE,
            t,
          );
        }
      }
      let eh =
        (((l = {})[(l.literal = 0)] = "literal"),
        (l[(l.object = 1)] = "object"),
        l);
      function ec(e) {
        return {
          create: () => ({
            get: (t) => e[t],
            set(t, r) {
              e[t] = r;
            },
          }),
        };
      }
      class ef {
        ast;
        locales;
        resolvedLocale;
        formatters;
        formats;
        message;
        formatterCache = { number: {}, dateTime: {}, pluralRules: {} };
        constructor(e, t = ef.defaultLocale, r, n) {
          var i;
          if (
            ((this.locales = t),
            (this.resolvedLocale = ef.resolveLocale(t)),
            "string" == typeof e)
          ) {
            if (((this.message = e), !ef.__parse))
              throw TypeError(
                "IntlMessageFormat.__parse must be set to process `message` of type `string`",
              );
            let { ...t } = n || {};
            this.ast = ef.__parse(e, { ...t, locale: this.resolvedLocale });
          } else this.ast = e;
          if (!Array.isArray(this.ast))
            throw TypeError("A message must be provided as a String or AST.");
          ((this.formats =
            ((i = ef.formats),
            r
              ? Object.keys(i).reduce(
                  (e, t) => {
                    var n, o;
                    return (
                      (e[t] =
                        ((n = i[t]),
                        (o = r[t])
                          ? {
                              ...n,
                              ...o,
                              ...Object.keys(n).reduce(
                                (e, t) => ((e[t] = { ...n[t], ...o[t] }), e),
                                {},
                              ),
                            }
                          : n)),
                      e
                    );
                  },
                  { ...i },
                )
              : i)),
            (this.formatters =
              (n && n.formatters) ||
              (function (e = { number: {}, dateTime: {}, pluralRules: {} }) {
                return {
                  getNumberFormat: h((...e) => new Intl.NumberFormat(...e), {
                    cache: ec(e.number),
                    strategy: g.variadic,
                  }),
                  getDateTimeFormat: h(
                    (...e) => new Intl.DateTimeFormat(...e),
                    { cache: ec(e.dateTime), strategy: g.variadic },
                  ),
                  getPluralRules: h((...e) => new Intl.PluralRules(...e), {
                    cache: ec(e.pluralRules),
                    strategy: g.variadic,
                  }),
                };
              })(this.formatterCache)));
        }
        format = (e) => {
          let t = this.formatToParts(e);
          if (1 === t.length) return t[0].value;
          let r = t.reduce(
            (e, t) => (
              e.length &&
              t.type === eh.literal &&
              "string" == typeof e[e.length - 1]
                ? (e[e.length - 1] += t.value)
                : e.push(t.value),
              e
            ),
            [],
          );
          return r.length <= 1 ? r[0] || "" : r;
        };
        formatToParts = (e) =>
          (function e(t, r, n, i, o, s, a) {
            if (1 === t.length && A(t[0]))
              return [{ type: eh.literal, value: t[0].value }];
            let l = [];
            for (let u of t) {
              if (A(u)) {
                l.push({ type: eh.literal, value: u.value });
                continue;
              }
              if (u.type === P.pound) {
                "number" == typeof s &&
                  l.push({
                    type: eh.literal,
                    value: n.getNumberFormat(r).format(s),
                  });
                continue;
              }
              let { value: t } = u;
              if (!(o && t in o)) throw new eu(t, a);
              let h = o[t];
              if (u.type === P.argument) {
                ((h &&
                  "string" != typeof h &&
                  "number" != typeof h &&
                  "bigint" != typeof h) ||
                  (h =
                    "string" == typeof h ||
                    "number" == typeof h ||
                    "bigint" == typeof h
                      ? String(h)
                      : ""),
                  l.push({
                    type: "string" == typeof h ? eh.literal : eh.object,
                    value: h,
                  }));
                continue;
              }
              if (B(u)) {
                let e =
                  "string" == typeof u.style
                    ? i.date[u.style]
                    : v(u.style)
                      ? u.style.parsedOptions
                      : void 0;
                l.push({
                  type: eh.literal,
                  value: n.getDateTimeFormat(r, e).format(h),
                });
                continue;
              }
              if (R(u)) {
                let e =
                  "string" == typeof u.style
                    ? i.time[u.style]
                    : v(u.style)
                      ? u.style.parsedOptions
                      : i.time.medium;
                l.push({
                  type: eh.literal,
                  value: n.getDateTimeFormat(r, e).format(h),
                });
                continue;
              }
              if (N(u)) {
                let e =
                  "string" == typeof u.style
                    ? i.number[u.style]
                    : O(u.style)
                      ? u.style.parsedOptions
                      : void 0;
                if (e && e.scale) {
                  let t = e.scale || 1;
                  if ("bigint" == typeof h) {
                    if (!Number.isInteger(t))
                      throw TypeError(
                        `Cannot apply fractional scale ${t} to bigint value. Scale must be an integer when formatting bigint.`,
                      );
                    h *= BigInt(t);
                  } else h *= t;
                }
                l.push({
                  type: eh.literal,
                  value: n.getNumberFormat(r, e).format(h),
                });
                continue;
              }
              if (L(u)) {
                let { children: t, value: h } = u,
                  c = o[h];
                if ("function" != typeof c) throw new el(h, "function", a);
                let f = c(e(t, r, n, i, o, s).map((e) => e.value));
                (Array.isArray(f) || (f = [f]),
                  l.push(
                    ...f.map((e) => ({
                      type: "string" == typeof e ? eh.literal : eh.object,
                      value: e,
                    })),
                  ));
              }
              if (I(u)) {
                let t = h,
                  s =
                    (Object.prototype.hasOwnProperty.call(u.options, t)
                      ? u.options[t]
                      : void 0) || u.options.other;
                if (!s) throw new ea(u.value, h, Object.keys(u.options), a);
                l.push(...e(s.value, r, n, i, o));
                continue;
              }
              if (M(u)) {
                let t = `=${h}`,
                  s = Object.prototype.hasOwnProperty.call(u.options, t)
                    ? u.options[t]
                    : void 0;
                if (!s) {
                  if (!Intl.PluralRules)
                    throw new es(
                      `Intl.PluralRules is not available in this environment.
Try polyfilling it using "@formatjs/intl-pluralrules"
`,
                      eo.MISSING_INTL_API,
                      a,
                    );
                  let e = "bigint" == typeof h ? Number(h) : h,
                    t = n
                      .getPluralRules(r, { type: u.pluralType })
                      .select(e - (u.offset || 0));
                  s =
                    (Object.prototype.hasOwnProperty.call(u.options, t)
                      ? u.options[t]
                      : void 0) || u.options.other;
                }
                if (!s) throw new ea(u.value, h, Object.keys(u.options), a);
                let c = "bigint" == typeof h ? Number(h) : h;
                l.push(...e(s.value, r, n, i, o, c - (u.offset || 0)));
                continue;
              }
            }
            return l.length < 2
              ? l
              : l.reduce((e, t) => {
                  let r = e[e.length - 1];
                  return (
                    r && r.type === eh.literal && t.type === eh.literal
                      ? (r.value += t.value)
                      : e.push(t),
                    e
                  );
                }, []);
          })(
            this.ast,
            this.locales,
            this.formatters,
            this.formats,
            e,
            void 0,
            this.message,
          );
        resolvedOptions = () => ({
          locale:
            this.resolvedLocale?.toString() ||
            Intl.NumberFormat.supportedLocalesOf(this.locales)[0],
        });
        getAst = () => this.ast;
        static memoizedDefaultLocale = null;
        static get defaultLocale() {
          return (
            ef.memoizedDefaultLocale ||
              (ef.memoizedDefaultLocale =
                new Intl.NumberFormat().resolvedOptions().locale),
            ef.memoizedDefaultLocale
          );
        }
        static resolveLocale = (e) => {
          if (void 0 === Intl.Locale) return;
          let t = Intl.NumberFormat.supportedLocalesOf(e);
          return new Intl.Locale(
            t.length > 0 ? t[0] : "string" == typeof e ? e : e[0],
          );
        };
        static __parse = ei;
        static formats = {
          number: {
            integer: { maximumFractionDigits: 0 },
            currency: { style: "currency" },
            percent: { style: "percent" },
          },
          date: {
            short: { month: "numeric", day: "numeric", year: "2-digit" },
            medium: { month: "short", day: "numeric", year: "numeric" },
            long: { month: "long", day: "numeric", year: "numeric" },
            full: {
              weekday: "long",
              month: "long",
              day: "numeric",
              year: "numeric",
            },
          },
          time: {
            short: { hour: "numeric", minute: "numeric" },
            medium: { hour: "numeric", minute: "numeric", second: "numeric" },
            long: {
              hour: "numeric",
              minute: "numeric",
              second: "numeric",
              timeZoneName: "short",
            },
            full: {
              hour: "numeric",
              minute: "numeric",
              second: "numeric",
              timeZoneName: "short",
            },
          },
        };
      }
      function em(...[e, t, r, n]) {
        let i;
        if (Array.isArray(t)) throw new E(b.INVALID_MESSAGE, void 0);
        if ("object" == typeof t) throw new E(b.INSUFFICIENT_PATH, void 0);
        if ("string" == typeof t) {
          let e = r || /'[{}]/.test(t) ? void 0 : t;
          if (e) return e;
        }
        let {
          cache: o,
          formats: s,
          formatters: a,
          globalFormats: l,
          locale: h,
          timeZone: c,
        } = n;
        a.getMessageFormat ||
          (a.getMessageFormat = T(
            (...e) => new ef(e[0], e[1], e[2], { formatters: a, ...e[3] }),
            o.message,
          ));
        try {
          i = a.getMessageFormat(
            t,
            h,
            (function (e, t, r) {
              let n = ef.formats.date,
                i = ef.formats.time,
                o = { ...e?.dateTime, ...t?.dateTime },
                s = {
                  date: { ...n, ...o },
                  time: { ...i, ...o },
                  number: { ...e?.number, ...t?.number },
                };
              return (
                r &&
                  ["date", "time"].forEach((e) => {
                    let t = s[e];
                    for (let [e, n] of Object.entries(t))
                      t[e] = { timeZone: r, ...n };
                  }),
                s
              );
            })(l, s, c),
            {
              formatters: {
                ...a,
                getDateTimeFormat: (e, t) =>
                  a.getDateTimeFormat(e, { ...t, timeZone: t?.timeZone ?? c }),
              },
            },
          );
        } catch (e) {
          throw new E(b.INVALID_MESSAGE, void 0);
        }
        let f = i.format(r);
        return (0, u.isValidElement)(f) ||
          Array.isArray(f) ||
          "string" == typeof f
          ? f
          : String(f);
      }
      function ep(...e) {
        return e.filter(Boolean).join(".");
      }
      function ed(e) {
        return ep(e.namespace, e.key);
      }
      function eg(e) {
        console.error(e);
      }
      function eE(e, t, r, n) {
        let i = ep(n, r);
        if (!t) throw Error(i);
        let o = t;
        return (
          r.split(".").forEach((t) => {
            let r = o[t];
            if (null == t || null == r) throw Error(i + ` (${e})`);
            o = r;
          }),
          o
        );
      }
      em.raw = !0;
      let eb = {
        second: 1,
        seconds: 1,
        minute: 60,
        minutes: 60,
        hour: 3600,
        hours: 3600,
        day: 86400,
        days: 86400,
        week: 604800,
        weeks: 604800,
        month: 2628e3,
        months: 2628e3,
        quarter: 7884e3,
        quarters: 7884e3,
        year: 31536e3,
        years: 31536e3,
      };
      var ey = r(7437);
      let eT = (0, u.createContext)(void 0);
      function e_({
        children: e,
        formats: t,
        getMessageFallback: r,
        locale: n,
        messages: i,
        now: o,
        onError: s,
        timeZone: a,
      }) {
        let l = (0, u.useContext)(eT),
          h = (0, u.useMemo)(() => l?.cache || y(), [n, l?.cache]),
          c = (0, u.useMemo)(() => l?.formatters || H(h), [h, l?.formatters]),
          f = (0, u.useMemo)(
            () => ({
              ...(function ({
                formats: e,
                getMessageFallback: t,
                messages: r,
                onError: n,
                ...i
              }) {
                return {
                  ...i,
                  formats: e || void 0,
                  messages: r || void 0,
                  onError: n || eg,
                  getMessageFallback: t || ed,
                };
              })({
                locale: n,
                formats: void 0 === t ? l?.formats : t,
                getMessageFallback: r || l?.getMessageFallback,
                messages: void 0 === i ? l?.messages : i,
                now: o || l?.now,
                onError: s || l?.onError,
                timeZone: a || l?.timeZone,
              }),
              formatters: c,
              cache: h,
            }),
            [h, t, c, r, n, i, o, s, l, a],
          );
        return (0, ey.jsx)(eT.Provider, { value: f, children: e });
      }
      function eH() {
        let e = (0, u.useContext)(eT);
        if (!e) throw Error(void 0);
        return e;
      }
      let eP = !1,
        eS = "undefined" == typeof window;
      function eA(e) {
        return (function (e, t, r) {
          let {
              cache: n,
              formats: i,
              formatters: o,
              getMessageFallback: s,
              locale: a,
              onError: l,
              timeZone: h,
            } = eH(),
            c = e["!"],
            f = "!" === t ? void 0 : t.slice(2);
          return (
            h ||
              eP ||
              !eS ||
              ((eP = !0), l(new E(b.ENVIRONMENT_FALLBACK, void 0))),
            (0, u.useMemo)(
              () =>
                (function (e) {
                  let t = (function (e, t, r) {
                    try {
                      if (!t) throw Error(void 0);
                      let n = r ? eE(e, t, r) : t;
                      if (!n) throw Error(r);
                      return n;
                    } catch (e) {
                      return new E(b.MISSING_MESSAGE, e.message);
                    }
                  })(e.locale, e.messages, e.namespace);
                  return (function ({
                    cache: e,
                    formats: t,
                    formatters: r,
                    getMessageFallback: n = ed,
                    locale: i,
                    messagesOrError: o,
                    namespace: s,
                    onError: a,
                    timeZone: l,
                  }) {
                    let h = o instanceof E;
                    function c(e, t, r, i) {
                      let o = new E(t, r);
                      return (a(o), i ?? n({ error: o, key: e, namespace: s }));
                    }
                    function f(f, m, p, d) {
                      let g;
                      if (h) {
                        if (!d)
                          return (a(o), n({ error: o, key: f, namespace: s }));
                        g = d;
                      } else
                        try {
                          g = eE(i, o, f, s);
                        } catch (e) {
                          if (!d) return c(f, b.MISSING_MESSAGE, e.message, d);
                          g = d;
                        }
                      try {
                        let n = ep(s, f);
                        return em(
                          n,
                          g,
                          m
                            ? (function (e) {
                                let t = {};
                                return (
                                  Object.keys(e).forEach((r) => {
                                    let n,
                                      i = 0,
                                      o = e[r];
                                    ((n =
                                      "function" == typeof o
                                        ? (e) => {
                                            let t = o(e);
                                            return (0, u.isValidElement)(t)
                                              ? (0, u.cloneElement)(t, {
                                                  key: r + i++,
                                                })
                                              : t;
                                          }
                                        : o),
                                      (t[r] = n));
                                  }),
                                  t
                                );
                              })(m)
                            : m,
                          {
                            cache: e,
                            formatters: r,
                            globalFormats: t,
                            formats: p,
                            locale: i,
                            timeZone: l,
                          },
                        );
                      } catch (r) {
                        let e, t;
                        return (
                          r instanceof E
                            ? ((e = r.code), (t = r.originalMessage))
                            : ((e = b.FORMATTING_ERROR), (t = r.message)),
                          c(f, e, t, d)
                        );
                      }
                    }
                    function m(e, t, r, n) {
                      let i = f(e, t, r, n);
                      return "string" != typeof i
                        ? c(e, b.INVALID_MESSAGE, void 0)
                        : i;
                    }
                    return (
                      (m.rich = f),
                      (m.markup = (e, t, r, n) => f(e, t, r, n)),
                      (m.raw = (e) => {
                        if (h)
                          return (a(o), n({ error: o, key: e, namespace: s }));
                        try {
                          return eE(i, o, e, s);
                        } catch (t) {
                          return c(e, b.MISSING_MESSAGE, t.message);
                        }
                      }),
                      (m.has = (e) => {
                        if (h) return !1;
                        try {
                          return (eE(i, o, e, s), !0);
                        } catch {
                          return !1;
                        }
                      }),
                      m
                    );
                  })({ ...e, messagesOrError: t });
                })({
                  cache: n,
                  formatters: o,
                  getMessageFallback: s,
                  messages: c,
                  namespace: f,
                  onError: l,
                  formats: i,
                  locale: a,
                  timeZone: h,
                }),
              [n, o, s, c, f, l, i, a, h],
            )
          );
        })({ "!": eH().messages }, e ? `!.${e}` : "!", "!");
      }
      function eN() {
        return eH().locale;
      }
      function eB() {
        let {
          formats: e,
          formatters: t,
          locale: r,
          now: n,
          onError: i,
          timeZone: o,
        } = eH();
        return (0, u.useMemo)(
          () =>
            (function (e) {
              let {
                _cache: t = y(),
                _formatters: r = H(t),
                formats: n,
                locale: i,
                onError: o = eg,
                timeZone: s,
              } = e;
              function a(e) {
                return (
                  e?.timeZone ||
                    (s
                      ? (e = { ...e, timeZone: s })
                      : o(new E(b.ENVIRONMENT_FALLBACK, void 0))),
                  e
                );
              }
              function l(e, t, r, n, i) {
                let s;
                try {
                  s = (function (e, t, r) {
                    let n;
                    if ("string" == typeof t) {
                      if (!(n = e?.[t])) {
                        let e = new E(b.MISSING_FORMAT, void 0);
                        throw (o(e), e);
                      }
                    } else n = t;
                    return (r && (n = { ...n, ...r }), n);
                  })(r, e, t);
                } catch {
                  return i();
                }
                try {
                  return n(s);
                } catch (e) {
                  return (o(new E(b.FORMATTING_ERROR, e.message)), i());
                }
              }
              function u(e, t, o) {
                return l(
                  t,
                  o,
                  n?.dateTime,
                  (t) => ((t = a(t)), r.getDateTimeFormat(i, t).format(e)),
                  () => String(e),
                );
              }
              function h() {
                return e.now
                  ? e.now
                  : (o(new E(b.ENVIRONMENT_FALLBACK, void 0)), new Date());
              }
              return {
                dateTime: u,
                number: function (e, t, o) {
                  return l(
                    t,
                    o,
                    n?.number,
                    (t) => r.getNumberFormat(i, t).format(e),
                    () => String(e),
                  );
                },
                relativeTime: function (e, t) {
                  try {
                    var n;
                    let o, s;
                    let a = {};
                    (t instanceof Date || "number" == typeof t
                      ? (o = new Date(t))
                      : t &&
                        ((o = null != t.now ? new Date(t.now) : h()),
                        (s = t.unit),
                        (a.style = t.style),
                        (a.numberingSystem = t.numberingSystem)),
                      o || (o = h()));
                    let l = (new Date(e).getTime() - o.getTime()) / 1e3;
                    (s ||
                      (s = (function (e) {
                        let t = Math.abs(e);
                        return t < 60
                          ? "second"
                          : t < 3600
                            ? "minute"
                            : t < 86400
                              ? "hour"
                              : t < 604800
                                ? "day"
                                : t < 2628e3
                                  ? "week"
                                  : t < 31536e3
                                    ? "month"
                                    : "year";
                      })(l)),
                      (a.numeric = "second" === s ? "auto" : "always"));
                    let u = ((n = s), Math.round(l / eb[n]));
                    return r.getRelativeTimeFormat(i, a).format(u, s);
                  } catch (t) {
                    return (o(new E(b.FORMATTING_ERROR, t.message)), String(e));
                  }
                },
                list: function (e, t, o) {
                  let s = [],
                    a = new Map(),
                    u = 0;
                  for (let t of e) {
                    let e;
                    ("object" == typeof t
                      ? ((e = String(u)), a.set(e, t))
                      : (e = String(t)),
                      s.push(e),
                      u++);
                  }
                  return l(
                    t,
                    o,
                    n?.list,
                    (e) => {
                      let t = r
                        .getListFormat(i, e)
                        .formatToParts(s)
                        .map((e) =>
                          "literal" === e.type
                            ? e.value
                            : a.get(e.value) || e.value,
                        );
                      return a.size > 0 ? t : t.join("");
                    },
                    () => String(e),
                  );
                },
                dateTimeRange: function (e, t, o, s) {
                  return l(
                    o,
                    s,
                    n?.dateTime,
                    (n) => (
                      (n = a(n)),
                      r.getDateTimeFormat(i, n).formatRange(e, t)
                    ),
                    () => [u(e), u(t)].join(" – "),
                  );
                },
              };
            })({
              formats: e,
              locale: r,
              now: n,
              onError: i,
              timeZone: o,
              _formatters: t,
            }),
          [e, t, n, r, i, o],
        );
      }
    },
  },
]);
