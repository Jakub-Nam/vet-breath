import { Directive, ElementRef, effect, inject, input } from '@angular/core';

/**
 * DELIBERATELY UNSAFE — XSS demonstration only. Do not use in real code.
 *
 * Assigns a raw, unsanitized string straight to the element's native
 * `innerHTML` sink. This bypasses Angular's DomSanitizer entirely (unlike the
 * `[innerHTML]` binding, which would strip `onerror`/`<script>`), so any HTML
 * in the value is parsed and its inline event handlers execute.
 *
 * The native `innerHTML` assignment is also exactly the sink that Trusted Types
 * guards: under an enforcing `require-trusted-types-for 'script'` CSP the line
 * below throws `TypeError` and the payload never reaches the DOM. That is the
 * intended fix — see context/changes/xss-demo-walkthrough.md.
 */
@Directive({
  selector: '[appRawHtml]',
})
export class RawHtml {
  private readonly element = inject<ElementRef<HTMLElement>>(ElementRef);
  public readonly appRawHtml = input<string>('');

  public constructor() {
    // effect() is the sanctioned place to leave Angular and touch the DOM.
    effect((): void => {
      this.element.nativeElement.innerHTML = this.appRawHtml();
    });
  }
}
