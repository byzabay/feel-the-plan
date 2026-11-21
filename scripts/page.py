"""Shared page chrome for lane-diagram pages: page format, 20px text floor, full-window diagrams that fit on open and resize."""
import html

CSS = r"""
:root{
  color-scheme:light;
  --ink:#16181c;--ink2:#30343a;--muted:#555b63;--rule:#d5d9df;--page:#eceef2;--card:#fff;
  --q:#dae8fc;--q-line:#6c8ebf;--q-ink:#1f3f6b;--n:#fff2cc;--n-line:#d6b656;--ex:#fff7cc;--ex-line:#d0b223;
  --red:#c62828;--red-bg:#fff4f4;--red-ink:#7d1717;
  --t-person:#ad1457;--t-you:#16181c;--t-mail:#5f6368;--t-tools:#00707a;--t-ai:#6a1b9a;--t-app:#1565c0;
  --t-db:#2e7d32;--t-cloud:#b45f06;--t-store:#8a5a00;--t-plain:#6b7078;--t-chat:#4752c4;
  --t-code:#00707a;--t-code2:#1565c0;
  --ease:cubic-bezier(.22,1,.36,1);
}
*{box-sizing:border-box}
html{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Helvetica,Arial,sans-serif;font-size:20px;line-height:1.45;color:var(--ink);background:var(--page)}
body{margin:0;font-size:20px}
p,h1,h2,h3,h4{margin:0}
h1,h2,h3,h4,strong,b,th{font-weight:600}
button{font:inherit;color:inherit;cursor:pointer}
button:focus-visible,.viewport:focus-visible,.bx:focus-visible,[role=tab]:focus-visible{outline:3px solid #1855a2;outline-offset:3px}
.muted{color:var(--muted)}
.fx{text-decoration:underline dotted;text-underline-offset:4px;text-decoration-thickness:2px}
.rd,.rd *:not(.tg):not(.bn):not(.own):not(.badge){color:var(--red)!important}
.rtag{display:inline-block;font-size:20px;font-weight:600;color:var(--red);border:1px solid var(--red);border-radius:6px;padding:0 8px;margin-left:8px;vertical-align:2px}
.stamp{background:var(--ink);color:#fff;padding:10px 24px;font-size:20px;display:flex;gap:16px;flex-wrap:wrap;justify-content:space-between;align-items:center}
.stamp .theme{display:inline-flex;border:1px solid #ffffff66;border-radius:7px;overflow:hidden}
.stamp .theme button{background:transparent;border:0;color:#fff;padding:4px 14px;font-size:20px}
.stamp .theme button.on{background:#fff;color:var(--ink);font-weight:600}
.frame{max-width:1720px;margin:auto;padding:24px 24px 64px;display:flex;flex-direction:column;gap:20px}
.intro h1{font-size:34px;line-height:1.15}
.intro p{margin-top:8px;max-width:1180px;font-size:20px;color:var(--ink2)}
.legend{display:flex;flex-wrap:wrap;gap:10px;align-items:center;font-size:20px}
.legend>span{background:var(--card);border:1px solid var(--rule);border-radius:999px;padding:4px 14px}
.legend .lq{background:var(--q);border-color:var(--q-line);color:var(--q-ink)}
.legend .ln{background:var(--n);border-color:var(--n-line)}
.legend .lex{background:var(--ex);border-color:var(--ex-line)}
.legend .lfix{border:2px solid var(--ink)}
.legend .lai{border:2px dashed var(--ink)}
.legend .lgap{border:2px solid var(--red);background:var(--red-bg);color:var(--red-ink)}
.legend .lred{border:2px solid var(--red);color:var(--red);font-weight:600}
.legend .ldot{border:2px dotted #7a7f87}
.legend .lstore{border:2px solid var(--ink);border-top-width:7px;background:#f6f7f9}
.legend .lhum{border:2px solid var(--ink);border-radius:999px}
.legend .lw{display:inline-flex;align-items:center;gap:10px}
.legend .lw i{display:inline-block;width:46px;height:0;border-top:3px solid var(--ink)}
.legend .lw i.login{border-top:3px dashed #7b3fa0}
.legend .lw i.data{border-top-color:#2e7d32}
.legend .lw i.move{border-top:3px dashed var(--red)}
.legend .lw i.loop{border-top:3px dashed #7a7f87}
.flow-tabs{display:flex;gap:8px;flex-wrap:wrap;position:sticky;top:0;z-index:30;background:var(--page);padding:10px 0;border-bottom:1px solid var(--rule)}
.flow-tabs button{border:1px solid var(--rule);background:var(--card);border-radius:8px;padding:8px 14px;font-size:20px;color:var(--ink2)}
.flow-tabs button.on{background:var(--ink);border-color:var(--ink);color:#fff;font-weight:600}
/* a selected tab must stay readable in every look, so nothing inside a tab button keeps its own colour */
.flow-tabs button.on *{color:inherit}
.flow-tabs button .n{font-weight:600;margin-right:8px}
.flow-tabs button.newt{border-color:var(--red);color:var(--red)}
.flow-tabs button.newt.on{background:var(--red);border-color:var(--red);color:#fff}
.screen{display:none;flex-direction:column;gap:18px}
.screen.on{display:flex}
.screen-h{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.screen-h h2{font-size:28px}
.badge{font-size:20px;font-weight:600;border-radius:6px;padding:2px 10px;white-space:nowrap;display:inline-block;border:1px solid transparent}
.badge.device{background:#e0f2f1;color:#00585f}
.badge.live{background:#e3eefc;color:#0d4a96}
.badge.svc{background:#f1f3f4;color:#3c4043;border-color:#dadce0}
.badge.cloud{background:#fff3e0;color:#8a4b00;border:1px dashed #8a4b00}
.badge.db{background:#e6f4e7;color:#1e5e22}
.badge.built{background:#e3f2e5;color:#24602b}
.badge.partly{background:#fde9d4;color:#8a3b00}
.badge.nb{background:#eceef1;color:#3d4046;border:1px dashed #7a7f87}
.badge.inflight{background:#fde7e7;color:#8e1b1b;border:1px solid var(--red)}
.what{border:1px solid var(--rule);border-left:5px solid var(--ink);background:var(--card);border-radius:10px;padding:14px 18px;display:flex;flex-direction:column;gap:8px}
.what h4,.rbox h4,.details-h{font-size:20px;color:var(--muted);font-weight:600}
.what blockquote{margin:0;border-left:4px solid var(--rule);padding-left:14px;color:var(--ink2)}
.today{border:1px dashed #9aa0a8;background:#f7f8fa;border-radius:10px;padding:12px 16px}
.today b.tl{font-size:20px;color:var(--muted);margin-right:8px}
.cols{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.cols3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.qs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.rbox{background:var(--card);border:1px solid var(--rule);border-radius:10px;padding:14px 18px}
.rbox ul,.rbox ol{margin:8px 0 0;padding-left:26px}
.rbox li{margin:4px 0}
.gapbox{border:2px solid var(--red);background:var(--red-bg);color:var(--red-ink);border-radius:10px;padding:14px 18px}
.gapbox b.t{display:block;margin-bottom:4px}
.gapbox ul{margin:6px 0 0;padding-left:26px}
.q{border:2px solid var(--q-line);background:var(--q);border-radius:10px;padding:14px 16px;display:flex;flex-direction:column;gap:6px;color:var(--q-ink)}
.q .qh{font-weight:600}
.q .ans{margin-top:4px;border-top:1px dashed var(--q-line);padding-top:8px}
.q .ans span{display:inline-block;min-width:180px;border-bottom:1px solid var(--q-ink);height:1em}
.q.rd{border-color:var(--red)}
.note{border:1px solid var(--n-line);background:var(--n);border-radius:10px;padding:14px 16px;display:flex;flex-direction:column;gap:8px}
.note textarea{width:100%;min-height:70px;border:1px solid var(--n-line);border-radius:7px;background:#fffbea;font:inherit;font-size:20px;padding:8px 10px;resize:vertical}
.ex{border:2px dotted #7a7f87;border-radius:10px;padding:10px 14px;background:#fafbfc;color:var(--ink2)}
.ex b.exl{display:block;font-size:20px;color:var(--muted)}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.go{border:0;background:none;padding:0;color:var(--q-ink);text-decoration:underline;text-underline-offset:4px;font-size:20px}
details.src{background:#f4f5f7;border:1px solid #c9ccd2;border-radius:10px;padding:10px 16px;font-size:20px;color:var(--ink2)}
details.src summary{cursor:pointer;font-weight:600}
details.src ul{margin:8px 0 0;padding-left:24px}
details.src code,code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:20px;word-break:break-word}
table.rt{border-collapse:collapse;width:100%;font-size:20px;background:var(--card)}
table.rt th,table.rt td{padding:10px 12px;border:1px solid var(--rule);text-align:left;vertical-align:top}
table.rt th{background:#f4f5f7;font-size:20px;color:var(--muted)}
table.rt td.after{background:#f6fbf6}
.yes{color:#8a3b00;font-weight:600}.no{color:#2e6b34;font-weight:600}
.own{display:inline-flex;align-items:center;gap:8px;border-radius:999px;padding:1px 12px;font-size:20px;font-weight:600;border:1px solid currentColor;white-space:nowrap;line-height:1.5}
.own::before{content:"";width:10px;height:10px;border-radius:50%;background:currentColor;flex:none}
.own.pink{color:#ad1457;background:#fce4ec}.own.green{color:#2e7d32;background:#e8f5e9}.own.blue{color:#1565c0;background:#e3f2fd}
.own.amber{color:#9a5800;background:#fff3e0}.own.purple{color:#6a1b9a;background:#f3e5f5}.own.teal{color:#00707a;background:#e0f7fa}
.own.slate{color:#4f6470;background:#eceff1}.own.orange{color:#bf360c;background:#fbe9e7}
.owners{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.kind{display:inline-block;font-size:20px;font-weight:600;border-radius:5px;padding:0 8px;border:2px solid var(--ink);background:#fff;white-space:nowrap}
.kind.ai{border-style:dashed}
[hidden]{display:none!important}

/* ===== lane diagram ===== */
.lanes{display:flex;flex-direction:column;gap:10px}
.lanes-tools{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}
.lanes-hint{color:var(--muted)}
.zoom{display:inline-flex;gap:6px}
.zoom button{border:1px solid var(--ink);border-radius:7px;background:#fff;padding:4px 14px;min-width:52px;font-size:20px}
.zoom button:hover{background:#f1f3f6}
.lanes-body{display:flex;align-items:flex-start;border:1px solid #b9bec6;border-radius:12px;overflow:hidden;background:#fff;box-shadow:0 1px 2px rgba(16,24,40,.06)}
.lane-labels{flex:none;position:relative;overflow:hidden;border-right:2px solid var(--ink);background:#fff;z-index:2}
.ll-stage,.stage{position:relative}
.ll-canvas,.canvas{position:absolute;top:0;left:0;transform-origin:0 0}
.ll-corner{position:absolute;left:12px;right:12px;display:flex;flex-direction:column;justify-content:flex-end;gap:2px;color:var(--muted);font-weight:600;font-size:20px}
.ll{position:absolute;left:0;right:0;border-top:1px solid var(--rule);padding:14px 16px 14px 24px;display:flex;flex-direction:column;justify-content:center;gap:2px;background:#fff}
.ll::before{content:"";position:absolute;left:0;top:0;bottom:0;width:9px;background:var(--tone)}
.ll-name{font-weight:600;font-size:20px;line-height:26px}
.ll-sub{color:var(--muted);font-size:20px;line-height:26px}
.viewport{flex:1;min-width:0;overflow-x:auto;overflow-y:hidden;background:#fff}
.band{position:absolute;left:0;border-top:1px solid var(--rule);background:color-mix(in srgb,var(--tone) 5%,#fff)}
.band.alt{background:color-mix(in srgb,var(--tone) 9%,#fff)}
.tone-person{--tone:var(--t-person)}.tone-you{--tone:var(--t-you)}.tone-mail{--tone:var(--t-mail)}.tone-tools{--tone:var(--t-tools)}
.tone-ai{--tone:var(--t-ai)}.tone-app{--tone:var(--t-app)}.tone-db{--tone:var(--t-db)}.tone-cloud{--tone:var(--t-cloud)}
.tone-store{--tone:var(--t-store)}.tone-plain{--tone:var(--t-plain)}.tone-chat{--tone:var(--t-chat)}
.tone-code{--tone:var(--t-code)}.tone-code2{--tone:var(--t-code2)}
.colhead{position:absolute;background:var(--ink);color:#fff;border-radius:7px;padding:10px 14px;display:flex;align-items:center;gap:10px;font-weight:600;font-size:20px;line-height:26px}
.colhead .lv{flex:none;border:1px solid #ffffff88;border-radius:5px;padding:0 6px;font-weight:600}
.colhead.rd{background:var(--red)}
.colhead.rd *{color:#fff!important}
.colex{position:absolute;background:var(--ex);border:1px solid var(--ex-line);border-radius:7px;padding:12px 16px;font-size:20px;line-height:26px;color:#3b3200}
.wires{position:absolute;top:0;left:0;overflow:visible}
.wires polyline{fill:none;stroke:var(--ink);stroke-width:2.5;stroke-linejoin:miter;transition:stroke-width 120ms var(--ease)}
.wires .w-login{stroke:#7b3fa0;stroke-dasharray:10 7}
.wires .w-data{stroke:#2e7d32}
.wires .w-move{stroke:var(--red);stroke-dasharray:10 7}
.wires .w-loop{stroke:#7a7f87;stroke-dasharray:7 7}
.wires .w-dash{stroke-dasharray:10 7}
.wires .w-red{stroke:var(--red)}
.wires polyline.hot{stroke-width:5}
.wl circle{fill:var(--ink);stroke:#fff;stroke-width:3}
.wl text{fill:#fff;font-size:20px;font-weight:600;font-family:inherit}
.wl.wl-login circle{fill:#7b3fa0}.wl.wl-data circle{fill:#2e7d32}.wl.wl-red circle,.wl.wl-move circle{fill:var(--red)}
.wl-text{fill:var(--ink);font-size:20px;font-weight:600;font-family:inherit;paint-order:stroke;stroke:#fff;stroke-width:7px;stroke-linejoin:round}
.wl-text.wl-red,.wl-text.wl-move{fill:var(--red)}
.wl-text.wl-login{fill:#5b2a78}.wl-text.wl-data{fill:#1f5f24}
.bx{position:absolute;display:flex;flex-direction:column;justify-content:center;gap:4px;padding:12px 14px;border-radius:9px;background:#fff;border:2px solid var(--ink);font-size:20px;line-height:26px;color:var(--ink);transition:box-shadow 120ms var(--ease)}
.bx .bt{font-weight:600}
.bx .bb{color:var(--ink2)}
.bx .bn,.dcard .bn{display:inline-block;min-width:30px;height:30px;line-height:30px;border-radius:15px;padding:0 7px;background:var(--ink);color:#fff;font-size:20px;font-weight:600;text-align:center;margin-right:8px;vertical-align:1px}
.bx.k-ai{border-style:dashed}
.bx.k-gap{border-color:var(--red);background:var(--red-bg);color:var(--red-ink)}
.bx.k-gap .bb{color:var(--red-ink)}
.bx.k-gap .bn{background:var(--red)}
.bx.k-todo{border:2px dashed var(--red);color:var(--red)}
.bx.k-todo .bb{color:var(--red)}
.bx.k-todo .bn{background:var(--red)}
.bx.k-human{border-radius:30px;padding-left:20px;padding-right:20px}
.bx.k-store{border-top-width:7px;background:#f6f7f9}
.bx.k-sys{border-width:3px}
.bx.k-note{background:var(--n);border:1px solid var(--n-line)}
.bx.k-q{background:var(--q);border:2px solid var(--q-line);color:var(--q-ink)}
.bx.k-q .bb{color:var(--q-ink)}
.bx.k-hub{background:var(--ink);color:#fff}
.bx.k-hub .bb{color:#e8eaed}
.bx.k-hub .bn{background:#fff;color:var(--ink)}
.bx.k-accent{background:#ff5a1f;color:#fff;border-color:var(--ink)}
.bx.k-accent .bb{color:#fff}
.bx.k-done{border-color:#9aa0a8;color:#5c6168}
.bx.k-done .bb{color:#5c6168}
.bx.made-up{border-style:dotted}
.bx.rd{border-color:var(--red)}
.bx.has-detail{cursor:pointer}
.bx.has-detail:hover,.bx.lit{box-shadow:0 0 0 5px rgba(21,101,192,.28)}
.tgs{display:flex;flex-wrap:wrap;gap:6px 8px;margin-top:4px}
.tg{display:inline-block;font-size:20px;font-weight:600;line-height:28px;border-radius:6px;padding:2px 10px;white-space:nowrap;border:1px solid transparent}
.tg-partly{background:#fde9d4;color:#8a3b00}
.tg-nb,.tg-notrun,.tg-later,.tg-idea{background:#eceef1;color:#3d4046;border:1px dashed #7a7f87}
.tg-parked,.tg-off{background:#eceef1;color:#3d4046}
.tg-inflight,.tg-next{background:#fde7e7;color:#8e1b1b;border-color:var(--red)}
.tg-built,.tg-live{background:#e3f2e5;color:#24602b}
.tg-ai{background:#f3e5f5;color:#5b1a7a;border:1px dashed #6a1b9a}
.tg-where{background:#f1f3f4;color:#3c4043;border-color:#dadce0}
.tg-device{background:#e0f2f1;color:#00585f}
.tg-app{background:#e3eefc;color:#0d4a96}
.tg-cloud{background:#fff3e0;color:#8a4b00;border:1px dashed #8a4b00}
.tg-repo{background:#fff;color:var(--ink);border:1px solid var(--ink)}
.tg-red{background:#fff;color:var(--red);border:1px solid var(--red)}
.tg-pink{color:#ad1457;background:#fce4ec;border-color:#ad1457}.tg-green{color:#2e7d32;background:#e8f5e9;border-color:#2e7d32}
.tg-blue{color:#1565c0;background:#e3f2fd;border-color:#1565c0}.tg-amber{color:#9a5800;background:#fff3e0;border-color:#9a5800}
.tg-purple{color:#6a1b9a;background:#f3e5f5;border-color:#6a1b9a}.tg-teal{color:#00707a;background:#e0f7fa;border-color:#00707a}
.tg-slate{color:#4f6470;background:#eceff1;border-color:#4f6470}.tg-orange{color:#bf360c;background:#fbe9e7;border-color:#bf360c}
.tg-run{background:#fff;color:var(--ink2);border:1px solid #9aa0a8}
.wire-key{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:8px 18px}
.wire-key li{display:flex;align-items:flex-start;gap:10px}
.wk-n{flex:none;min-width:34px;height:34px;border-radius:17px;background:var(--ink);color:#fff;font-weight:600;display:grid;place-items:center;padding:0 6px}
.wk-k{flex:none;width:40px;height:0;margin-top:17px;border-top:3px solid var(--ink)}
.wk-login{border-top:3px dashed #7b3fa0}.wk-data{border-top-color:#2e7d32}.wk-move{border-top:3px dashed var(--red)}.wk-loop{border-top:3px dashed #7a7f87}
.details{display:flex;flex-direction:column;gap:12px}
.dgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:14px}
.dcard{background:var(--card);border:1px solid var(--rule);border-left:5px solid var(--ink);border-radius:10px;padding:14px 16px;display:flex;flex-direction:column;gap:8px}
.dcard h4{font-size:20px}
.dcard .dwhere{color:var(--muted)}
.dcard .dbody ul,.dcard .dbody ol{margin:4px 0 0;padding-left:24px}
.dcard.rd{border-left-color:var(--red)}
.dcard.lit{box-shadow:0 0 0 5px rgba(21,101,192,.28)}
.dshow{align-self:flex-start;border:1px solid var(--rule);background:#fff;border-radius:7px;padding:4px 12px;font-size:20px}
.panel{background:var(--card);border:1px solid var(--rule);border-radius:12px;padding:18px;display:flex;flex-direction:column;gap:14px}
.panel>h3{font-size:24px}
@media(max-width:1000px){.cols,.cols3,.qs{grid-template-columns:1fr}}
@media(max-width:700px){.frame{padding:16px 12px 48px}.intro h1{font-size:28px}.lane-labels{display:none}}
@media print{.flow-tabs,.zoom,.note textarea{display:none}.screen{display:flex!important;break-before:page}.viewport{overflow:visible}}

/* text keeps its margins (frame 1720px); diagrams span the window with a small fixed margin */
.lanes{width:calc(var(--vw,100vw) - 32px);margin-left:calc(50% - var(--vw,100vw) / 2 + 16px);align-self:flex-start}
body{overflow-x:hidden}
@media(max-width:700px){.lanes{width:calc(var(--vw,100vw) - 24px);margin-left:calc(50% - var(--vw,100vw) / 2 + 12px)}}
/* app mock screens (.c-root …): a generic chat/card mock-up for sketching a screen */
.answers{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:12px;margin-top:8px}
.lbox{border:2px solid var(--ink);border-radius:9px;padding:12px 14px;background:#fff}
.lbox b.t{display:block;margin-bottom:4px}
.lbox.ai{border-style:dashed}
.c-root{--background:#fff;--foreground:#1c1d1f;--card:#fff;--muted-foreground:#6b6b6b;--border:#e5e5e5;--primary:#1c1d1f;--primary-foreground:#fafafa;--chrome:#f4f5f7;--page:#e9ebef;--pill-bg:#f3ecd2;--pill-tx:#6b5300;--face-bg:#f9e0e6;--face-tx:#8f2a44;background:var(--page);color:var(--foreground);border-radius:18px;padding:10px;font-size:20px}
.c-root.dark{--background:#1a1a1a;--foreground:#f2f2f2;--card:#262626;--muted-foreground:#b3b3b3;--border:#ffffff22;--primary:#e6e6e6;--primary-foreground:#262626;--chrome:#222;--page:#121212;--pill-bg:#4a3f1c;--pill-tx:#f1dc9a;--face-bg:#4a2530;--face-tx:#f5c2cf}
.c-shell{background:var(--chrome);border:1px solid var(--border);border-radius:18px;overflow:hidden}
.c-pane{background:var(--background);margin:10px;border:1px solid var(--border);border-radius:14px}
.c-chead{display:flex;align-items:center;gap:12px;padding:12px 16px;border-bottom:1px solid var(--border);flex-wrap:wrap}
.c-chead .ttl{font-weight:600}
.c-chead .sub{color:var(--muted-foreground)}
.c-feed{padding:16px;display:flex;flex-direction:column;gap:14px}
.c-face{width:40px;height:40px;border-radius:50%;display:inline-grid;place-items:center;font-size:20px;font-weight:600;flex:none;background:var(--face-bg);color:var(--face-tx)}
.c-msg{display:flex;gap:12px;align-items:flex-start}
.c-msg .who{font-weight:600}
.c-msg .t{color:var(--muted-foreground);font-weight:400;margin-left:8px}
.c-ecard{border-radius:14px;box-shadow:0 0 0 1px color-mix(in srgb,var(--foreground) 14%,transparent);background:var(--card);overflow:hidden;margin-top:8px}
.c-ecard .eh{padding:12px 14px 6px;font-weight:600;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.c-ecard .eb{padding:6px 14px 12px;display:flex;flex-direction:column;gap:8px}
.c-ecard .ef{border-top:1px solid var(--border);padding:10px 14px;display:flex;gap:10px;flex-wrap:wrap}
.c-erow{display:grid;grid-template-columns:100px 1fr;gap:10px;align-items:center}
.c-erow>span:first-child{color:var(--muted-foreground)}
.c-box{border:1px solid var(--border);border-radius:8px;padding:8px 10px;background:var(--background)}
.c-btn{display:inline-flex;align-items:center;height:42px;padding:0 16px;border-radius:10px;border:1px solid transparent;font-size:20px;font-weight:500;background:var(--primary);color:var(--primary-foreground)}
.c-btn.c-out{background:var(--background);color:var(--foreground);border-color:var(--border)}
.c-pill{display:inline-flex;align-items:center;height:30px;padding:0 12px;border-radius:999px;font-size:20px;font-weight:600;background:var(--pill-bg);color:var(--pill-tx)}
.stack-gap{display:flex;flex-direction:column;gap:12px}

.c-rowsb{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
.c-acts{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.c-tbl{width:100%;border-collapse:collapse;margin-top:8px;font-size:20px}
.c-tbl th,.c-tbl td{border-bottom:1px solid var(--border);padding:8px 10px;text-align:left;vertical-align:top}
.c-tbl th{color:var(--muted-foreground);font-weight:600}
.c-sw{display:inline-block;width:44px;height:26px;border-radius:13px;background:var(--border);position:relative;vertical-align:middle}
.c-sw.on{background:var(--primary)}
.c-sw.on::after{content:"";position:absolute;right:3px;top:3px;width:20px;height:20px;border-radius:50%;background:var(--primary-foreground)}
.c-i{display:inline-grid;place-items:center;width:30px;height:30px;border-radius:50%;border:1px solid var(--border);font-size:20px;color:var(--muted-foreground);cursor:help;margin-left:6px}
.c-test{display:flex;flex-direction:column;gap:8px}
.c-root .c-erow{grid-template-columns:220px 1fr;margin-top:8px}
.c-root .c-box{margin-top:12px}
.fx-box{border-style:dotted}
.q.yq{background:#eef4fd}
.q.yq blockquote{margin:6px 0;border-left:4px solid var(--q-line);padding-left:12px;color:var(--ink2)}
.panel ol li,.rbox ol li{margin:6px 0}
.intro p,.what,.today,.ex{max-width:1720px}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

JS = r"""
(function () {
  "use strict";
  var tabs = Array.prototype.slice.call(document.querySelectorAll("#flowTabs [role=tab]"));
  function show(n, keepScroll) {
    var i, screens = document.querySelectorAll(".screen");
    for (i = 0; i < tabs.length; i++) { var sel = tabs[i].getAttribute("data-go") === String(n); tabs[i].classList.toggle("on", sel); tabs[i].setAttribute("aria-selected", String(sel)); tabs[i].tabIndex = sel ? 0 : -1; }
    for (i = 0; i < screens.length; i++) screens[i].classList.toggle("on", screens[i].id === "screen-" + n);
    if (!keepScroll) window.scrollTo(0, 0);
    fitWideDefaults();
  }
  function zoomOf(d) { return parseFloat(d.getAttribute("data-z") || "1"); }
  function setZoom(d, z) {
    z = Math.max(0.2, Math.min(1.6, z));
    d.setAttribute("data-z", String(z));
    var w = +d.getAttribute("data-w"), h = +d.getAttribute("data-h"), lw = +d.getAttribute("data-lw");
    var cv = d.querySelector(".canvas"), st = d.querySelector(".stage");
    cv.style.transform = "scale(" + z + ")"; st.style.width = (w * z) + "px"; st.style.height = (h * z) + "px";
    var lc = d.querySelector(".ll-canvas"), ls = d.querySelector(".ll-stage"), lab = d.querySelector(".lane-labels");
    lc.style.transform = "scale(" + z + ")"; ls.style.width = (lw * z) + "px"; ls.style.height = (h * z) + "px"; lab.style.width = (lw * z) + "px";
    var b = d.querySelector('[data-zoom="reset"]'); if (b) b.textContent = Math.round(z * 100) + "%";
  }
  function fit(d) {
    var vp = d.querySelector(".lanes-body"); if (!vp || !vp.clientWidth) return;
    var w = +d.getAttribute("data-w"), lw = +d.getAttribute("data-lw");
    setZoom(d, Math.min(1, (vp.clientWidth - 4) / (w + lw)));
  }
  function fitWideDefaults() {
    document.querySelectorAll(".screen.on .lanes").forEach(function (d) { if (d.getAttribute("data-manual") !== "1") fit(d); });
  }
  document.addEventListener("click", function (e) {
    var go = e.target.closest("[data-go]");
    if (go) { show(go.getAttribute("data-go")); return; }
    var th = e.target.closest("[data-theme]");
    if (th) {
      var dark = th.getAttribute("data-theme") === "dark";
      document.querySelectorAll(".c-root").forEach(function (r) { r.classList.toggle("dark", dark); });
      document.querySelectorAll("[data-theme]").forEach(function (b) { b.classList.toggle("on", b === th); });
      return;
    }
    var zb = e.target.closest("[data-zoom]");
    if (zb) {
      var d = document.getElementById(zb.getAttribute("data-for")), k = zb.getAttribute("data-zoom");
      if (k === "in") { d.setAttribute("data-manual", "1"); setZoom(d, zoomOf(d) + 0.1); }
      else if (k === "out") { d.setAttribute("data-manual", "1"); setZoom(d, zoomOf(d) - 0.1); }
      else if (k === "reset") { d.setAttribute("data-manual", "1"); setZoom(d, 1); }
      else { d.setAttribute("data-manual", "0"); fit(d); }
      return;
    }
    var sh = e.target.closest("[data-show]");
    if (sh) { var bx = document.getElementById(sh.getAttribute("data-show")); if (bx) { reveal(bx); flash(bx); } return; }
    var box = e.target.closest(".bx[data-detail]");
    if (box) { openDetail(box); }
  });
  document.addEventListener("keydown", function (e) {
    var box = e.target.closest && e.target.closest(".bx[data-detail]");
    if (box && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); openDetail(box); }
  });
  function openDetail(box) { var c = document.getElementById(box.getAttribute("data-detail")); if (c) { c.scrollIntoView({ behavior: "smooth", block: "center" }); flash(c); } }
  function flash(el) { el.classList.add("lit"); setTimeout(function () { el.classList.remove("lit"); }, 1600); }
  function reveal(bx) {
    var d = bx.closest(".lanes"), vp = d.querySelector(".viewport"), z = zoomOf(d);
    var left = parseFloat(bx.style.left) * z, w = parseFloat(bx.style.width) * z;
    vp.scrollLeft = Math.max(0, left - (vp.clientWidth - w) / 2);
    d.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  document.addEventListener("mouseover", function (e) {
    var bx = e.target.closest && e.target.closest(".bx"); if (!bx || bx.contains(e.relatedTarget)) return;
    var id = bx.id; bx.closest(".canvas").querySelectorAll('polyline[data-source="' + id + '"],polyline[data-target="' + id + '"]').forEach(function (p) { p.classList.add("hot"); });
  });
  document.addEventListener("mouseout", function (e) {
    var bx = e.target.closest && e.target.closest(".bx"); if (!bx || bx.contains(e.relatedTarget)) return;
    bx.closest(".canvas").querySelectorAll("polyline.hot").forEach(function (p) { p.classList.remove("hot"); });
  });
  var bar = document.getElementById("flowTabs");
  if (bar) bar.addEventListener("keydown", function (e) {
    var cur = e.target.closest('[role="tab"]'); if (!cur) return;
    var idx = tabs.indexOf(cur), next = idx;
    if (e.key === "ArrowRight" || e.key === "ArrowDown") next = (idx + 1) % tabs.length;
    else if (e.key === "ArrowLeft" || e.key === "ArrowUp") next = (idx - 1 + tabs.length) % tabs.length;
    else if (e.key === "Home") next = 0; else if (e.key === "End") next = tabs.length - 1; else return;
    e.preventDefault(); show(tabs[next].getAttribute("data-go"), true); tabs[next].focus();
  });
  function setVw() { document.documentElement.style.setProperty("--vw", document.documentElement.clientWidth + "px"); }
  setVw();
  document.querySelectorAll(".lanes").forEach(function (d) { setZoom(d, 1); });
  fitWideDefaults();
  var rt = null;
  window.addEventListener("resize", function () { setVw(); clearTimeout(rt); rt = setTimeout(fitWideDefaults, 120); });
})();
"""


def esc(s):
    return html.escape(s, quote=True)


def badge(kind, text):
    return f'<span class="badge {kind}">{text}</span>'


def quote(text, who):
    return f'<blockquote>"{text}" <span class="muted">({who})</span></blockquote>'


def what(story, quotes=(), red=False):
    r = ' class="rd"' if red else ""
    q = "".join(quote(t, w) for t, w in quotes)
    return f'<div class="what"><h4>User story</h4><p{r}>{story}</p>{q}</div>'


def qbox(qid, q, pick, why, red=False, who="My pick"):
    cls = "q rd" if red else "q"
    return (f'<div class="{cls}" id="q-{qid}"><div class="qh">{qid} · {q}</div><div><strong>{who}:</strong> {pick}</div>'
            f'<div>Why: {why}</div><div class="ans">Your answer: <span></span></div></div>')


def note_box():
    return ('<div class="note"><strong>Your notes (not saved, reply in chat)</strong>'
            '<textarea aria-label="Your notes" placeholder="Type while you review, then paste into chat. Reloading loses it."></textarea></div>')


def sources(items):
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f'<details class="src"><summary>Sources (for the build lanes)</summary><ul>{lis}</ul></details>'


def tabs_nav(tabs, label):
    out = [f'<nav class="flow-tabs" id="flowTabs" role="tablist" aria-label="{esc(label)}">']
    for i, t in enumerate(tabs):
        key, num, name = t["key"], t["num"], t["name"]
        cls = []
        if i == 0:
            cls.append("on")
        if t.get("new"):
            cls.append("newt")
        c = f' class="{" ".join(cls)}"' if cls else ""
        out.append(f'<button type="button" data-go="{key}"{c} id="tab-{key}" role="tab" aria-controls="screen-{key}" '
                   f'aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}"><span class="n">{num}</span>{name}</button>')
    out.append("</nav>")
    return "\n".join(out)


def section(key, first, body, textonly=False):
    """textonly=True only for a list-only tab (All questions, Your questions): every other v4 tab leads with a diagram (verify.py)."""
    on = " on" if first else ""
    to = ' data-textonly="list"' if textonly else ""
    return f'<section class="screen{on}" id="screen-{key}" role="tabpanel" aria-labelledby="tab-{key}"{to}>\n{body}\n</section>'


def page(title, comment, stamp, header, legend, nav, sections_html, footer, theme_toggle=False, look=None):
    """The page. look="v4" is the current look for new pages; look="v3" (the default) keeps the older, plainer output."""
    if (look or DEFAULT_LOOK) == "v4":
        return _page_v4(title, comment, stamp, header, legend, nav, sections_html, footer, theme_toggle)
    return _page_v3(title, comment, stamp, header, legend, nav, sections_html, footer, theme_toggle)


def _page_v3(title, comment, stamp, header, legend, nav, sections_html, footer, theme_toggle=False):
    theme = ('<div class="theme" role="group" aria-label="Mock screen theme"><button type="button" data-theme="light">Light</button>'
             '<button type="button" data-theme="dark" class="on">Dark</button></div>') if theme_toggle else ""
    return f"""<!-- {comment} -->
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:">
<title>{esc(title)}</title>
<style>{CSS}</style>
<noscript><style>.screen{{display:flex!important}}</style></noscript>
</head>
<body>
<div class="stamp"><div>{stamp}</div>{theme}</div>
<div class="frame">
{header}
{legend}
{nav}
{sections_html}
<p class="muted">{footer}</p>
</div>
<script>{JS}</script>
</body>
</html>
"""


# =====================================================================================================
# v4 look: line icons, status and model chips, formatted prompts, a hover/tap popover instead of the card grid,
# and an always-on light/dark toggle. page(..., look="v4") turns it on.
# Older pages (look="v3", the default) render byte-identical to before.
# =====================================================================================================
import re  # noqa: E402

from lucide_sprite import NAMES as _ICON_LIST, SPRITE  # noqa: E402
import pageedit  # noqa: E402  (edit mode + Cmd+S save into the file)

DEFAULT_LOOK = "v3"   # existing generators keep their output; new pages pass look="v4"
ICON_NAMES = frozenset(_ICON_LIST)

ACC, ACC_INK = '#2f6fdb', '#2459b3'
MONO = 'ui-monospace,Menlo,Consolas,monospace'
CHEV = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' "
        "stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m9 18 6-6-6-6'/%3E%3C/svg%3E\")")

V = 'html body .v4look'          # page or section scope; the extra html/body wins ties with html.night rules
POP = 'html body .hpop.v4look'   # popover scope


def both(sel):
    return ','.join(f'{s} {x.strip()}' for s in (V, POP) for x in sel.split(','))


_TOKENS = ('--acc:#2f6fdb;--acc-ink:#2459b3;--hair:rgba(22,24,28,.12);--surf:#f4f5f6;'
           '--ok-bg:#e5f1e7;--ok-ink:#1f5f2a;--wait-bg:#fbeedb;--wait-ink:#7a4300;--stop-bg:#fbe8e8;--stop-ink:#8e1b1b;--stop-line:#c62828')
_TOKENS_NIGHT = ('--acc:#7fa8f0;--acc-ink:#a3c1f7;--hair:rgba(232,233,235,.16);--surf:#26282c;'
                 '--ok-bg:#1d3324;--ok-ink:#8fd0a0;--wait-bg:#3a2c12;--wait-ink:#e8b866;--stop-bg:#3d1f1c;--stop-ink:#f6b3ab;--stop-line:#ff7b6b')

V4_CSS = f"""
/* ===== v4 look ===== */
.v4sprite{{position:absolute;width:0;height:0;overflow:hidden}}
.v4look,.hpop.v4look{{{_TOKENS}}}
html.night .v4look,html.night .hpop.v4look{{{_TOKENS_NIGHT}}}
.bxi,.tgi,.ico{{width:20px;height:20px;flex:none;display:inline-block;vertical-align:-4px}}
@media(prefers-reduced-motion:reduce){{.hpop,.hpop-x,details.prompt>summary::before{{transition:none!important}}}}

/* diagram: boxes keep the router's padding, line height and size; only colour, icons and rings change */
{V} .bx .bt .bxi{{margin-right:8px}}
{V} .bx.has-detail:hover,{V} .bx.lit,{V} .bx.pinned{{box-shadow:0 0 0 4px color-mix(in srgb,var(--acc) 32%,transparent)}}
{V} .bx:focus-visible,{V} button:focus-visible,{V} .viewport:focus-visible{{outline:3px solid var(--acc);outline-offset:3px}}
{V} .colhead{{background:color-mix(in srgb,var(--ink) 7%,var(--card));color:var(--ink)}}
{V} .colhead .lv{{border-color:color-mix(in srgb,var(--ink) 28%,transparent)}}
{V} .colhead.rd{{background:var(--red);color:#fff}}
{V} .ll-name{{display:block}}
{both('.lli')}{{display:inline-flex;align-items:center;justify-content:center;width:28px;height:26px;margin-right:8px;border-radius:6px;vertical-align:top;
 background:color-mix(in srgb,var(--tone,var(--ink)) 12%,var(--card));color:var(--tone,var(--ink))}}
html.night body .v4look .lli,html.night body .hpop.v4look .lli{{background:color-mix(in srgb,var(--tone,var(--ink)) 24%,#17181a);color:color-mix(in srgb,var(--tone,var(--ink)) 50%,#fff)}}
{V} .ll .lli-lane{{display:flex;width:64px;height:64px;margin:0 0 4px;border-radius:12px}}
{V} .ll .lli-lane .bxi{{width:40px;height:40px}}
{V} .details{{display:none}}

/* tags on the boxes: status colour only where it means something, everything else neutral */
{V} .tg{{display:inline-flex;align-items:center;gap:6px;font-weight:500;background:var(--surf);color:var(--ink2);border:1px solid var(--hair)}}
{V} .tg-built,{V} .tg-live{{background:var(--ok-bg);color:var(--ok-ink);border-color:transparent}}
{V} .tg-partly,{V} .tg-notrun,{V} .tg-parked,{V} .tg-off{{background:var(--wait-bg);color:var(--wait-ink);border-color:transparent}}
{V} .tg-inflight,{V} .tg-next{{background:var(--stop-bg);color:var(--stop-ink);border-color:transparent}}
{V} .tg-red{{background:var(--card);color:var(--stop-ink);border-color:var(--stop-line)}}
{V} .tg-later,{V} .tg-nb,{V} .tg-idea{{border-style:dashed;border-color:color-mix(in srgb,var(--muted) 70%,transparent)}}
{V} .tg-ai{{border-style:dashed}}

/* facts table (hidden cards below and the popover) */
{both('dl.facts')}{{gap:0 16px}}
{both('dl.facts>dt,dl.facts>dd')}{{padding:8px 0;border-top:1px solid var(--hair)}}
{both('dl.facts>dt:first-of-type,dl.facts>dd:first-of-type')}{{border-top:0;padding-top:0}}
{both('dl.facts>dt')}{{display:flex;gap:8px;align-items:flex-start;color:var(--muted);font-weight:500}}
{both('dl.facts>dt>.ico')}{{margin-top:4px}}
{both('.schip,.mchip')}{{display:inline-flex;align-items:center;gap:6px;padding:0 8px;border-radius:6px;border:1px solid transparent;font-weight:500;white-space:nowrap;vertical-align:baseline}}
{both('.schip')}{{margin-right:8px}}
{both('.s-live')}{{background:var(--ok-bg);color:var(--ok-ink)}}
{both('.s-wait')}{{background:var(--wait-bg);color:var(--wait-ink)}}
{both('.s-next')}{{background:var(--stop-bg);color:var(--stop-ink)}}
{both('.s-idea')}{{background:var(--surf);color:var(--ink2);border:1px dashed color-mix(in srgb,var(--muted) 70%,transparent)}}
{both('.s-held')}{{background:var(--surf);color:var(--ink2)}}
{both('.mchip')}{{background:var(--surf);border-color:var(--hair);color:var(--ink)}}
{both('.mchip.m-code')}{{color:var(--ink2)}}
{both('.go')}{{color:var(--acc-ink)}}
{both('[data-icon]:not(li)>.ico:first-child')}{{margin-right:8px}}

/* formatted prompts: <details class="prompt"><summary>…</summary><div class="mdp">…</div></details> */
{both('details.prompt')}{{border:1px solid var(--hair);border-radius:8px;padding:0;background:var(--card);margin-top:8px}}
{both('details.prompt>summary')}{{list-style:none;display:flex;align-items:center;gap:8px;padding:8px 12px;cursor:pointer;font-weight:500;color:var(--acc-ink)}}
{both('details.prompt>summary::-webkit-details-marker')}{{display:none}}
{both('details.prompt>summary::before')}{{content:"";width:20px;height:20px;flex:none;background:currentColor;
 -webkit-mask:{CHEV} center/20px 20px no-repeat;mask:{CHEV} center/20px 20px no-repeat;transition:transform 150ms var(--ease)}}
{both('details.prompt[open]>summary')}{{border-bottom:1px solid var(--hair)}}
{both('details.prompt[open]>summary::before')}{{transform:rotate(90deg)}}
{both('details.prompt>summary:focus-visible')}{{outline:3px solid var(--acc);outline-offset:2px;border-radius:8px}}
{both('details.prompt>p.muted')}{{padding:8px 16px 0}}
{both('.mdp')}{{padding:12px 16px 16px;max-height:520px;overflow:auto;display:flex;flex-direction:column;gap:8px;color:var(--ink)}}
{both('.mdp h5')}{{font-size:20px;font-weight:600;margin:8px 0 0}}
{both('.mdp h5:first-child')}{{margin-top:0}}
{both('.mdp p')}{{margin:0}}
{both('.mdp ul,.mdp ol')}{{margin:0;padding-left:28px}}
{both('.mdp li')}{{margin:4px 0}}
{both('.mdp strong')}{{font-weight:600}}
{both('.mdp code')}{{font-family:{MONO};font-size:20px;background:var(--surf);border-radius:4px;padding:0 4px}}
{both('.mdp .ph')}{{font-family:{MONO};font-size:20px;background:color-mix(in srgb,var(--acc) 12%,var(--card));color:var(--acc-ink);border-radius:4px;padding:0 4px;white-space:nowrap}}
{both('.mdp pre')}{{white-space:pre-wrap;word-break:break-word;font-family:{MONO};font-size:20px;line-height:1.45;margin:0;padding:8px 12px;background:var(--surf);border-radius:8px;max-height:none;overflow:visible}}
{both('.mdp pre.mdtable')}{{white-space:pre;overflow-x:auto}}

/* mini flow: <ol class="miniflow"><li data-icon="NAME">text</li>…</ol> */
{both('ol.miniflow')}{{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;align-items:center;gap:8px 0}}
{both('ol.miniflow>li')}{{position:relative;display:inline-flex;align-items:center;gap:8px;padding:4px 12px;border:1px solid var(--hair);border-radius:8px;background:var(--card);color:var(--ink)}}
{both('ol.miniflow>li>.ico')}{{color:var(--ink2)}}
{both('ol.miniflow>li:not(:last-child)')}{{margin-right:36px}}
{both('ol.miniflow>li:not(:last-child)::after')}{{content:"";position:absolute;right:-28px;top:50%;width:20px;height:20px;margin-top:-10px;background:var(--muted);
 -webkit-mask:{CHEV} center/20px 20px no-repeat;mask:{CHEV} center/20px 20px no-repeat}}

/* popover (all tabs: close button, tap, sheet on phones; v4 look only when its box is in a v4look section) */
html body .hpop{{visibility:hidden;transition:opacity 150ms var(--ease),transform 150ms var(--ease),visibility 0s linear 150ms}}
html body .hpop.on{{visibility:visible;transition:opacity 150ms var(--ease),transform 150ms var(--ease),visibility 0s linear 0s}}
html body .hpop.sheet{{left:16px;right:16px;top:auto;bottom:16px;width:auto;max-height:72vh}}
.hpop-h{{display:flex;gap:12px;align-items:flex-start;justify-content:space-between}}
.hpop-h h4{{flex:1;min-width:0}}
.hpop-x{{flex:none;width:36px;height:36px;display:inline-grid;place-items:center;padding:0;border:1px solid var(--rule);border-radius:8px;background:var(--card);color:var(--ink2);transition:background-color 150ms var(--ease)}}
.hpop-x:hover{{background:color-mix(in srgb,var(--ink) 6%,var(--card))}}
.hpop-x:active{{transform:scale(.98)}}
.hpop-x:focus-visible{{outline:3px solid {ACC};outline-offset:2px}}
{POP}{{border:1px solid var(--hair);border-radius:12px;padding:16px 20px 20px;background:var(--card);box-shadow:0 12px 32px rgba(16,24,40,.14)}}
html.night body .hpop.v4look{{background:#1d1e21;box-shadow:0 12px 32px rgba(0,0,0,.5)}}
{POP} .hpop-h h4 .bxi{{margin-right:8px}}
{POP} .bn{{display:inline-block;min-width:28px;height:28px;line-height:28px;border-radius:14px;padding:0 8px;background:var(--ink);color:var(--card);font-weight:600;text-align:center;margin-right:8px;vertical-align:1px}}
{POP} .dwhere{{display:flex;align-items:center;color:var(--muted);margin:4px 0 12px}}
{POP} .hint{{color:var(--muted);margin:12px 0 0}}
"""


V4_BASE_CSS = r"""

.hpop{position:fixed;z-index:60;left:0;top:0;width:min(640px,calc(100vw - 32px));max-height:min(76vh,760px);overflow:auto;background:var(--card);color:var(--ink);
 border:1px solid var(--rule);border-radius:12px;padding:16px 20px;font-size:20px;line-height:1.45;opacity:0;transform:translateY(4px);pointer-events:none}
.hpop.on{opacity:1;transform:none;pointer-events:auto}
.hpop h4{margin:0 0 4px;font-size:20px;font-weight:600}
.hpop .dwhere{color:var(--muted);margin:0 0 8px}
.hpop .hint{color:var(--muted);margin:8px 0 0}
dl.facts{display:grid;grid-template-columns:max-content minmax(0,1fr);gap:4px 16px;margin:4px 0 0}
dl.facts dt{color:var(--muted);font-weight:500}
dl.facts dd{margin:0}
.stampbtns{display:inline-flex;gap:8px;flex-wrap:wrap}
.nightbtn{border:1px solid #ffffff66;background:transparent;color:#fff;border-radius:999px;padding:4px 16px;font-size:20px;transition:background-color 150ms var(--ease)}
.nightbtn:hover{background:#ffffff1f}
html.night{color-scheme:dark;--ink:#e8e9eb;--ink2:#c9ccd1;--muted:#a3a8b0;--rule:#3a3d42;--page:#121314;--card:#1d1e21;
 --q:#1b2a40;--q-line:#5b7fb3;--q-ink:#cfe0ff;--n:#2e2a17;--n-line:#8a7638;--ex:#2b2814;--ex-line:#8a7638;--red:#ff7b6b;--red-bg:#3d1f1c;--red-ink:#f6b3ab}
html.night body,html.night{background:var(--page);color:var(--ink)}
html.night .stamp{background:#000;color:#d0d2d6}
html.night .flow-tabs button.on{background:#e8e9eb;border-color:#e8e9eb;color:#121314}
html.night .what,html.night .rbox,html.night .panel,html.night .dcard,html.night details.prompt{background:var(--card)}
html.night .note textarea{background:#1a1810;color:var(--ink)}
html.night table.rt{background:var(--card)}html.night table.rt th{background:#26272b;color:var(--muted)}html.night table.rt td.after{background:#18261a}
html.night details.src{background:#1a1b1e;border-color:#3a3d42;color:var(--ink2)}
html.night .today{background:#1a1b1e;border-color:#555}html.night .ex{background:#1a1b1e}
html.night .lanes-body,html.night .viewport,html.night .lane-labels,html.night .ll{background:#17181a}
html.night .band{background:color-mix(in srgb,var(--tone) 10%,#17181a)}html.night .band.alt{background:color-mix(in srgb,var(--tone) 16%,#17181a)}
html.night .bx{background:#1f2023;color:var(--ink);border-color:#d7d9dc}
html.night .bx .bb{color:var(--ink2)}
html.night .bx.k-store{background:#26282c}
html.night .bx.k-gap{background:var(--red-bg);border-color:var(--red);color:var(--red-ink)}
html.night .bx.k-q{background:var(--q);color:var(--q-ink)}
html.night .bx.k-hub{background:#e8e9eb;color:#121314}html.night .bx.k-hub .bb{color:#2a2b2e}
html.night .bx .bn,html.night .dcard .bn,html.night .wk-n{background:#e8e9eb;color:#121314}
html.night .colex{color:#efe3a6}
html.night .wires polyline{stroke:#d7d9dc}html.night .wl circle{fill:#d7d9dc;stroke:#17181a}html.night .wl text{fill:#121314}
html.night .wl-text{fill:#e8e9eb;stroke:#17181a}
html.night .zoom button,html.night .dshow{background:#1f2023;color:var(--ink);border-color:#555}
html.night .badge.live{background:#16263d;color:#a9c8f5}html.night .badge.nb{background:#26282c;color:#c9ccd1}html.night .badge.partly{background:#3a2c12;color:#e8b866}
html.night .badge.built{background:#1d3324;color:#8fd0a0}html.night .badge.inflight{background:#3d1f1c;color:#f6b3ab}
html.night .legend>span{background:var(--card)}
html.night .kind,html.night .lbox{background:var(--card)}
"""

NIGHT_HEAD_JS = ('try{if(localStorage.getItem("diagram-night")==="1"||(localStorage.getItem("diagram-night")===null&&'
                 'matchMedia("(prefers-color-scheme: dark)").matches))document.documentElement.classList.add("night")}catch(e){}')

NIGHT_JS = r"""
(function () {
  var b = document.getElementById("v4night"), h = document.documentElement;
  if (!b) return;
  function sync() { var on = h.classList.contains("night"); b.setAttribute("aria-pressed", on ? "true" : "false"); b.textContent = on ? "Day mode" : "Night mode"; }
  b.addEventListener("click", function () { h.classList.toggle("night"); try { localStorage.setItem("diagram-night", h.classList.contains("night") ? "1" : "0"); } catch (e) {} sync(); });
  sync();
})();
"""

V4_JS = r"""
(function () {
  "use strict";
  var canHover = !!(window.matchMedia && matchMedia("(hover: hover) and (pointer: fine)").matches);
  var pop = document.createElement("div");
  pop.className = "hpop"; pop.id = "hpop";
  pop.setAttribute("role", "dialog"); pop.setAttribute("aria-labelledby", "hpop-title");
  document.body.appendChild(pop);
  var cur = null, pinned = false, hideT = null;
  var XSVG = '<svg class="ico" aria-hidden="true" focusable="false"><use href="#i-x"/></svg>';
  function isV4(b) { return !!(b && b.closest(".v4look")); }
  Array.prototype.forEach.call(document.querySelectorAll(".v4look .bx[data-detail]"), function (b) {
    b.setAttribute("aria-label", (b.getAttribute("aria-label") || "").replace(/: show details below$/, ": open details"));
    b.setAttribute("aria-haspopup", "dialog"); b.setAttribute("aria-expanded", "false");
  });
  function narrow() { return window.innerWidth < 720; }
  function place(box) {
    if (pinned && narrow()) { pop.classList.add("sheet"); pop.style.left = ""; pop.style.top = ""; return; }
    pop.classList.remove("sheet");
    var r = box.getBoundingClientRect(), pw = pop.offsetWidth, ph = pop.offsetHeight, vw = window.innerWidth, vh = window.innerHeight, m = 16;
    var x = r.right + 12;
    if (x + pw > vw - m) x = r.left - 12 - pw;
    if (x < m) x = Math.max(m, Math.min(vw - m - pw, r.left));
    var y = r.top;
    if (y + ph > vh - m) y = vh - m - ph;
    if (y < m) y = m;
    pop.style.left = x + "px"; pop.style.top = y + "px";
  }
  function fill(box) {
    var c = document.getElementById(box.getAttribute("data-detail"));
    if (!c) return false;
    var h = c.querySelector("h4"), w = c.querySelector(".dwhere"), d = c.querySelector(".dbody"), v4 = isV4(box);
    var hint = pinned ? "" : (v4 ? "Click the box to keep this open" : (canHover ? "Click the box to open this card under the diagram" : ""));
    pop.innerHTML = '<div class="hpop-h"><h4 id="hpop-title">' + (h ? h.innerHTML : "") + '</h4>'
      + '<button type="button" class="hpop-x" aria-label="Close details">' + XSVG + "</button></div>"
      + (w ? '<p class="dwhere">' + w.innerHTML + "</p>" : "")
      + (d ? '<div class="hpop-b">' + d.innerHTML + "</div>" : "")
      + (hint ? '<p class="hint">' + hint + "</p>" : "");
    pop.classList.toggle("v4look", v4);
    return true;
  }
  function mark(box, on) {
    if (!box) return;
    box.classList.toggle("pinned", on);
    if (isV4(box)) box.setAttribute("aria-expanded", on ? "true" : "false");
  }
  function show(box, pin) {
    clearTimeout(hideT);
    if (cur && cur !== box) mark(cur, false);
    pinned = !!pin; cur = box;
    if (!fill(box)) { cur = null; pinned = false; return; }
    pop.classList.toggle("pinned", pinned);
    mark(box, pinned);
    pop.classList.add("on");
    place(box);
  }
  function hide(restore) {
    clearTimeout(hideT);
    pop.classList.remove("on", "pinned", "sheet");
    var b = cur; cur = null; pinned = false;
    if (b) { mark(b, false); if (restore && b.focus) b.focus({ preventScroll: true }); }
  }
  function hideSoon() {
    if (pinned) return;
    clearTimeout(hideT);
    hideT = setTimeout(function () { if (!pinned) hide(false); }, 220);
  }
  if (canHover) {
    document.addEventListener("mouseover", function (e) {
      var b = e.target.closest && e.target.closest(".bx[data-detail]");
      if (!b || pinned) return;
      if (b !== cur) show(b, false); else clearTimeout(hideT);
    });
    document.addEventListener("mouseout", function (e) {
      var b = e.target.closest && e.target.closest(".bx[data-detail]"), to = e.relatedTarget;
      if (b && !pinned && !(to && (b.contains(to) || pop.contains(to)))) hideSoon();
    });
    pop.addEventListener("mouseenter", function () { clearTimeout(hideT); });
    pop.addEventListener("mouseleave", hideSoon);
    document.addEventListener("focusin", function (e) {
      var b = e.target.closest && e.target.closest(".bx[data-detail]");
      if (b && !pinned) show(b, false);
    });
    document.addEventListener("focusout", function (e) {
      var b = e.target.closest && e.target.closest(".bx[data-detail]");
      if (b && !pinned) hideSoon();
    });
  }
  /* capture phase: runs before the page's own click handler */
  document.addEventListener("click", function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    if (pop.contains(t)) {
      if (t.closest(".hpop-x")) { e.preventDefault(); hide(true); return; }
      if (t.closest("[data-go]")) setTimeout(function () { hide(false); }, 0);   /* the page's handler still switches the tab */
      return;
    }
    var b = t.closest(".bx[data-detail]");
    if (b && (isV4(b) || !canHover)) {
      e.stopPropagation();   /* the page would scroll to the card below, which v4 hides */
      if (pinned && cur === b) { hide(false); return; }
      show(b, true);
      return;
    }
    if (pinned) hide(false);
  }, true);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && pop.classList.contains("on")) { hide(pinned || pop.contains(document.activeElement)); return; }
    var b = e.target.closest && e.target.closest(".bx[data-detail]");
    if (b && isV4(b) && (e.key === "Enter" || e.key === " ")) {
      e.preventDefault(); e.stopPropagation();
      show(b, true);
      var x = pop.querySelector(".hpop-x"); if (x) x.focus({ preventScroll: true });
    }
  }, true);
  window.addEventListener("scroll", function () { if (cur && pop.classList.contains("on")) place(cur); }, { passive: true });
  window.addEventListener("resize", function () { if (cur && pop.classList.contains("on")) place(cur); });
})();
(function () {
  "use strict";
  /* Open the tab a link names: page.html#screen-KEY, #tab-KEY or #KEY, so links from elsewhere land on the right tab. */
  function openFromHash() {
    var m = (location.hash || "").match(/^#(?:screen-|tab-)?([a-z0-9]+)$/i);
    if (!m) return;
    var t = document.getElementById("tab-" + m[1]);
    if (!t) return;
    var d = t.closest && t.closest("details"); if (d && !d.open) d.open = true;
    t.click();
  }
  window.addEventListener("hashchange", openFromHash);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", openFromHash); else openFromHash();
})();
"""

# ------------------------------------------------------------------ decorate()
FACT_ICONS = {
    'what it does': 'info', 'runs on': 'server', 'model': 'cpu', 'logic': 'git-branch',
    'data in': 'arrow-down-to-line', 'data out': 'arrow-up-from-line', 'metrics': 'bar-chart-3', 'cost': 'coins',
    'status': 'badge-check', 'test': 'flask-conical', 'your idea': 'lightbulb', 'evidence': 'quote', 'gap': 'triangle-alert',
    'held instead': 'circle-pause', 'how': 'list-tree', 'versions': 'history', 'why it fits': 'target',
    'rationale': 'message-square-text', 'the question': 'message-square-text', 'what you see': 'monitor',
    'who uses it': 'users', 'size rule': 'scale', 'before switching on': 'shield-check',
}
FACT_PREFIX = (('next release', 'clock'), ('after ', 'clock'), ('replay', 'history'), ('re-scored', 'bar-chart-3'))

# (leading phrase, chip class, icon); first match wins, checked at the very start of the Status value
STATUS_RULES = (
    (r'Code live', 's-wait', 'circle-pause'),
    (r'[Oo]ff', 's-wait', 'circle-pause'),
    (r'Shipped(?:, switched off|, off)?', 's-wait', 'circle-pause'),
    (r'Next release(?:, switched off|, off)?', 's-next', 'clock'),
    (r'Live', 's-live', 'circle-check'),
    (r'Exists', 's-live', 'circle-check'),
    (r'Idea', 's-idea', 'lightbulb'),
    (r'Held', 's-held', 'circle-pause'),
)
MODELS = ('Gemini Deep Research', 'Gemini Flash-Lite', 'Flash-Lite', 'Gemini', 'Claude', 'Opus', 'Sonnet', 'Haiku', 'GPT',
          'Llama', 'Mistral')   # names that get a model chip in a "Model" fact; pass models=... to decorate() to change


def _model_re(models):
    return re.compile(r'(?<![\w-])(' + '|'.join(re.escape(m) for m in sorted(models, key=len, reverse=True)) + r')(?![\w-])')


_MODEL_RE = _model_re(MODELS)
_CODE_LEAD = re.compile(r'^(\s*)(None(?:[.:]\s*[Cc]ode only)?|[Cc]ode only)(?![\w-])')
_CODE_ANY = re.compile(r'(?<![\w-])([Cc]ode only)(?![\w-])')


def icon(name, cls='ico'):
    if name not in ICON_NAMES:
        name = 'dot'
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'


def _plain(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def _fact_icon(label):
    k = _plain(label).lower()
    if k in FACT_ICONS:
        return FACT_ICONS[k]
    for p, n in FACT_PREFIX:
        if k.startswith(p):
            return n
    return 'dot'


def _status(dd):
    if 'class="schip' in dd:
        return dd
    for pat, cls, ic in STATUS_RULES:
        m = re.match(r'(\s*)(' + pat + r')(?![\w-])', dd)
        if m:
            rest = re.sub(r'^[.;:,]\s*', '', dd[m.end():]).lstrip()
            return f'{m.group(1)}<span class="schip {cls}">{icon(ic)}{m.group(2)}</span>{rest}'
    return dd


def _models(dd):
    if 'class="mchip' in dd:
        return dd
    parts = re.split(r'(<[^>]+>)', dd)
    seen, in_code, first_text = set(), 0, True
    for i, p in enumerate(parts):
        if p.startswith('<'):
            if re.match(r'<(code|pre|a)\b', p):
                in_code += 1
            elif re.match(r'</(code|pre|a)>', p):
                in_code = max(0, in_code - 1)
            continue
        if in_code or not p:
            continue
        if first_text:
            first_text = False
            m = _CODE_LEAD.match(p)
            if m:
                seen.add('code')
                p = f'{m.group(1)}<span class="mchip m-code">{icon("code")}{m.group(2)}</span>' + p[m.end():]
                head, tail = p[:p.index('</span>') + 7], p[p.index('</span>') + 7:]
                parts[i] = head + _model_sub(tail, seen)
                continue
        parts[i] = _model_sub(p, seen)
    return ''.join(parts)


def _model_sub(text, seen):
    def rep(m):
        n = m.group(1)
        if n in seen:
            return n
        seen.add(n)
        return f'<span class="mchip">{n}</span>'

    def rep_code(m):
        if 'code' in seen:
            return m.group(1)
        seen.add('code')
        return f'<span class="mchip m-code">{icon("code")}{m.group(1)}</span>'
    out = _MODEL_RE.sub(rep, text)
    return _CODE_ANY.sub(rep_code, out) if '<span class="mchip m-code"' not in out else out


_PAIR = re.compile(r'(<dt\b[^>]*>)(.*?)(</dt>)(\s*)(<dd\b[^>]*>)(.*?)(</dd>)', re.S)


def _facts(m):
    def pair(p):
        dt_o, label, dt_c, ws, dd_o, val, dd_c = p.groups()
        key = _plain(label).lower()
        if '<svg class="ico' not in label:
            label = icon(_fact_icon(label)) + label
        if key == 'status':
            val = _status(val)
        elif key == 'model':
            val = _models(val)
        return f'{dt_o}{label}{dt_c}{ws}{dd_o}{val}{dd_c}'
    return m.group(1) + _PAIR.sub(pair, m.group(2)) + m.group(3)


_FACTS = re.compile(r'(<dl class="facts"[^>]*>)(.*?)(</dl>)', re.S)
_DATA_ICON = re.compile(r'(<([a-zA-Z][\w-]*)\b[^>]*?\sdata-icon="([a-z0-9-]+)"[^>]*>)(?!\s*<svg class="ico)')


def decorate(section_html, models=None):
    """Post-process rendered sections: icons on [data-icon] and fact labels, status and model chips. Safe to run twice."""
    global _MODEL_RE
    keep = _MODEL_RE
    if models is not None:
        _MODEL_RE = _model_re(models)
    try:
        s = _DATA_ICON.sub(lambda m: m.group(1) + icon(m.group(3)), section_html)
        return _FACTS.sub(_facts, s)
    finally:
        _MODEL_RE = keep


# ---------------------------------------------------------------- v4 markup helpers
def facts(rows):
    """A detail card's facts table: [(label, value html)]. decorate() adds the label icons and chips."""
    return '<dl class="facts">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows) + "</dl>"


def miniflow(steps):
    """A small left-to-right flow inside a card or section: [(icon, text)]."""
    return '<ol class="miniflow">' + "".join(f'<li data-icon="{esc(ic)}">{tx}</li>' for ic, tx in steps) + "</ol>"


def go(key, text, icon_name="workflow"):
    """A button that opens another tab (e.g. a step's own sub-flow tab from its box's card); works inside the popover."""
    return f'<button type="button" class="go" data-go="{esc(key)}" data-icon="{esc(icon_name)}">{text}</button>'


def _md_inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\{\{([A-Za-z0-9_]+)\}\}", r'<span class="ph">{{\1}}</span>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def md_html(text):
    """A prompt's own markdown drawn as text (headings, lists, bold, code, {{PLACEHOLDERS}}); never show raw markdown."""
    out, para, items, code, tbl = [], [], [None, []], None, []

    def flush():
        if para:
            out.append("<p>" + "<br>".join(_md_inline(x) for x in para) + "</p>")
            para.clear()
        if items[0]:
            out.append(f"<{items[0]}>" + "".join(f"<li>{_md_inline(x)}</li>" for x in items[1]) + f"</{items[0]}>")
            items[0], items[1] = None, []
        if tbl:
            out.append('<pre class="mdtable">' + html.escape("\n".join(tbl), quote=False) + "</pre>")
            tbl.clear()
    for ln in text.split("\n"):
        st = ln.rstrip()
        if code is not None:
            if st.strip().startswith("```"):
                out.append("<pre>" + html.escape("\n".join(code), quote=False) + "</pre>")
                code = None
            else:
                code.append(ln)
            continue
        if st.strip().startswith("```"):
            flush()
            code = []
            continue
        if not st.strip():
            flush()
            continue
        if st.lstrip().startswith("|"):
            if para or items[0]:
                flush()
            tbl.append(st)
            continue
        m = re.match(r"^\s*(#{1,6})\s+(.*)", st)
        if m:
            flush()
            out.append(f"<h5>{_md_inline(m.group(2))}</h5>")
            continue
        m = re.match(r"^\s*[-*\u2022]\s+(.*)", st) or re.match(r"^\s*\d+[.)]\s+(.*)", st)
        if m:
            kind = "ul" if re.match(r"^\s*[-*\u2022]\s", st) else "ol"
            if para or tbl or (items[0] and items[0] != kind):
                flush()
            items[0] = kind
            items[1].append(m.group(1))
            continue
        if items[0] and re.match(r"^\s{2,}\S", ln):
            items[1][-1] += " " + st.strip()
            continue
        if items[0] or tbl:
            flush()
        para.append(st.strip())
    if code is not None:
        out.append("<pre>" + html.escape("\n".join(code), quote=False) + "</pre>")
    flush()
    return '<div class="mdp">' + "".join(out) + "</div>"


def prompt_block(summary, text, note=""):
    """A fold-out that shows a prompt formatted (md_html), with an optional one-line note above it."""
    n = f'<p class="muted">{note}</p>' if note else ""
    return f'<details class="prompt"><summary>{summary}</summary>{n}{md_html(text)}</details>'


def _page_v4(title, comment, stamp, header, legend, nav, sections_html, footer, theme_toggle):
    stamp_v4 = (stamp + '</div><div class="stampbtns"><button class="nightbtn" id="v4night" type="button" aria-pressed="false">'
                'Night mode</button>')
    h = _page_v3(title, comment, stamp_v4, header, legend, nav, decorate(sections_html), footer, theme_toggle)
    h = h.replace("<style>", "<script>" + NIGHT_HEAD_JS + "</script>\n<style>", 1)
    h = h.replace("</style>", V4_BASE_CSS + V4_CSS + "</style>", 1)
    h = h.replace("<body>", "<body>\n" + SPRITE, 1)
    h = h.replace('<div class="frame">', '<div class="frame v4look">', 1)
    h = h.replace("</body>", "<script>" + V4_JS + NIGHT_JS + "</script>\n</body>", 1)
    return pageedit.apply(h)
