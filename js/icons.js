// AoE4 アイコンのSVGスプライト（build時に生成されたものを切り出し）
export const SPRITE = `<svg style="display:none" xmlns="http://www.w3.org/2000/svg">
<symbol id="i-hp" viewBox="0 0 24 24"><path d="M12 21C5 16.5 3 13 3 9.8A4.6 4.6 0 0 1 12 7.4 4.6 4.6 0 0 1 21 9.8C21 13 19 16.5 12 21Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-melee" viewBox="0 0 24 24"><path d="M12 1.8 14.4 6.5V13.5H9.6V6.5Z" fill="currentColor" stroke="none"/><path d="M7 14.2h10M12 14.2v4.4"/><circle cx="12" cy="20.4" r="1.7" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-ranged" viewBox="0 0 24 24"><path d="M4 20 19 5M13 4.5h6.5V11M4 20l.2-4M4 20l4-.2"/></symbol>
<symbol id="i-siege" viewBox="0 0 24 24"><path d="M2.5 20C5 9.5 13 5.5 19 8.5"/><circle cx="19.5" cy="10.5" r="2.6" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-fire" viewBox="0 0 24 24"><path d="M12 2.5c4 5 6 7.5 6 11a6 6 0 0 1-12 0c0-2 1-3.5 2.5-5 .3 1.6 1 2.5 2 2.5 1.2 0 1.8-1.6 1.5-8.5Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-dps" viewBox="0 0 24 24"><path d="M13.5 2 4 13.5h6L9 22l10-12h-6.5Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-int" viewBox="0 0 24 24"><circle cx="12" cy="14" r="7.5"/><path d="M12 14V9.5M9 2h6M19.5 7 21 5.5"/></symbol>
<symbol id="i-range" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="3.8"/><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-armm" viewBox="0 0 24 24"><path d="M12 2.4 20 6v5.6c0 5-4.4 8.2-8 10-3.6-1.8-8-5-8-10V6Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-armr" viewBox="0 0 24 24"><path d="M12 2.4 20 6v5.6c0 5-4.4 8.2-8 10-3.6-1.8-8-5-8-10V6Z"/><path d="M9.2 14.8 14.8 9.2M11.5 9.2h3.3v3.3" stroke-width="1.7"/></symbol>
<symbol id="i-speed" viewBox="0 0 24 24"><path d="M3 7.5h11M3 12h7.5M3 16.5h9.5"/><path d="M15.5 6.5 21 12l-5.5 5.5"/></symbol>
<symbol id="i-pop" viewBox="0 0 24 24"><circle cx="12" cy="7.5" r="3.7"/><path d="M4.5 20.5c0-4.2 3.4-6.5 7.5-6.5s7.5 2.3 7.5 6.5"/></symbol>
<symbol id="i-time" viewBox="0 0 24 24"><path d="M6.5 2.5h11M6.5 21.5h11M8.5 2.5v3.6L12 10.4l3.5-4.3V2.5M8.5 21.5v-3.6L12 13.6l3.5 4.3v3.6"/></symbol>
<symbol id="i-food" viewBox="0 0 24 24"><path d="M12 22V8"/><path d="M12 16.5c-3.4 0-5.4-2.2-5.4-5.2 3.4 0 5.4 2.2 5.4 5.2Zm0 0c3.4 0 5.4-2.2 5.4-5.2-3.4 0-5.4 2.2-5.4 5.2Z" fill="currentColor" stroke="none"/><path d="M12 10.5c-3 0-4.8-2-4.8-4.6 3 0 4.8 2 4.8 4.6Zm0 0c3 0 4.8-2 4.8-4.6-3 0-4.8 2-4.8 4.6Z" fill="currentColor" stroke="none"/><path d="M12 6.4c1.7-1.6 1.7-3.4 0-4.8-1.7 1.4-1.7 3.2 0 4.8Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-wood" viewBox="0 0 24 24"><path d="M12 2.5 6 11h3.2L4.5 18.5h15L14.8 11H18Z" fill="currentColor" stroke="none"/><path d="M12 18.5v3"/></symbol>
<symbol id="i-gold" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="3.6" fill="#1b1713" stroke="none"/></symbol>
<symbol id="i-stone" viewBox="0 0 24 24"><path d="M4 16.5 8 7l7-2.5 5.5 6-2.5 8-9 1Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="a-inf" viewBox="0 0 24 24"><path d="M4.5 16.8a7.5 7.5 0 0 1 15 0v3.7h-5.6v-3.7h-3.8v3.7H4.5Z" fill="currentColor" stroke="none"/><path d="M12 9V4.5" stroke-width="2"/></symbol>
<symbol id="a-cav" viewBox="0 0 24 24"><path d="M6.5 21.5V13a5.5 5.5 0 0 1 11 0v8.5"/><circle cx="8" cy="17.5" r="1.2" fill="currentColor" stroke="none"/><circle cx="16" cy="17.5" r="1.2" fill="currentColor" stroke="none"/></symbol>
<symbol id="a-camel" viewBox="0 0 24 24"><path d="M2.5 19.5v-1.8c0-2 1.4-3.6 3.2-3.6s3.2 1.6 3.2 3.6c0-2 1.4-3.6 3.2-3.6s3.2 1.6 3.2 3.6v1.8"/><path d="M15.3 17.7V9.4c0-1.6 1.2-2.9 2.8-2.9h2.4"/></symbol>
<symbol id="a-eleph" viewBox="0 0 24 24"><path d="M3.5 20.5V14a6.2 6.2 0 0 1 12.4 0v6.5"/><path d="M15.9 15c2.9.5 3.7 3.4 1.8 5.5"/><circle cx="7.8" cy="13.2" r="2.4"/><path d="M13.4 19l2.2 1.6"/></symbol>
<symbol id="a-siege" viewBox="0 0 24 24"><path d="M2.5 21h16"/><circle cx="7.5" cy="17.2" r="3.4"/><path d="M5.8 14.4 16.5 5.2"/><path d="M14.6 3h6v5.2h-6Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="a-ship" viewBox="0 0 24 24"><path d="M2.5 16.5h19l-3 4.5H5.5Z" fill="currentColor" stroke="none"/><path d="M12 16V3M12.8 4.5 19 14.5h-6.2"/></symbol>
<symbol id="a-relig" viewBox="0 0 24 24"><path d="M12 3v18M6 9.5h12"/></symbol>
<symbol id="a-worker" viewBox="0 0 24 24"><path d="M3 21 11 13"/><path d="M11.5 5.5 19 13l-2.8 2.8L8.7 8.3Z"/></symbol>
<symbol id="a-gun" viewBox="0 0 24 24"><circle cx="10" cy="15.5" r="6.2" fill="currentColor" stroke="none"/><path d="M14.6 11c1.5-1.6 2-3 1.6-4.6"/><path d="M18.2 4.4l2.6-1.4M19.6 7.4h3M18.6 1.6l.8 2.4"/></symbol>
<symbol id="a-melee" viewBox="0 0 24 24"><path d="M12 1.8 14.4 6.5V13.5H9.6V6.5Z" fill="currentColor" stroke="none"/><path d="M7 14.2h10M12 14.2v4.4"/><circle cx="12" cy="20.4" r="1.7" fill="currentColor" stroke="none"/></symbol>
<symbol id="a-ranged" viewBox="0 0 24 24"><path d="M4 20 19 5M13 4.5h6.5V11M4 20l.2-4M4 20l4-.2"/></symbol>
<symbol id="a-massive" viewBox="0 0 24 24"><path d="M7.5 7.5h9v9h-9Z" fill="currentColor" stroke="none"/><path d="M4 8.5V4h4.5M15.5 4H20v4.5M20 15.5V20h-4.5M8.5 20H4v-4.5"/></symbol>
<symbol id="a-scout" viewBox="0 0 24 24"><path d="M2 12s3.8-6 10-6 10 6 10 6-3.8 6-10 6-10-6-10-6Z"/><circle cx="12" cy="12" r="2.6" fill="currentColor" stroke="none"/></symbol>
<symbol id="a-spear" viewBox="0 0 24 24"><path d="M3.5 20.5 15.5 8.5"/><path d="M22 2 14 5.5 18.5 10Z" fill="currentColor" stroke="none"/><path d="M9 12.5 11.5 15"/></symbol>
<symbol id="a-xbow" viewBox="0 0 24 24"><path d="M3 6Q12 13 21 6"/><path d="M3 6H21"/><path d="M12 3.5V21M9.2 21h5.6"/></symbol>
<symbol id="a-bow" viewBox="0 0 24 24"><path d="M6 3.5a13 13 0 0 1 0 17"/><path d="M6 3.5 6 20.5"/><path d="M6 12h13M15.5 8.5 19 12l-3.5 3.5"/></symbol>
<symbol id="a-heavy" viewBox="0 0 24 24"><path d="M12 2.4 20 6v5.6c0 5-4.4 8.2-8 10-3.6-1.8-8-5-8-10V6Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="a-light" viewBox="0 0 24 24"><path d="M19.5 3.5C10 4 4.5 9.5 4.5 18v2.5"/><path d="M19.5 3.5c.5 8-4.5 13-11.5 13.5"/></symbol>
</svg>`;
