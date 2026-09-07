import { httpResource } from '@angular/common/http';
import { Component } from '@angular/core';
import { environment } from '../../../environments/environment';
import { VERSION } from '../../core/version';

interface Health {
  status: string;
  version: string;
}

@Component({
  selector: 'app-footer',
  imports: [],
  templateUrl: './footer.html',
  styleUrl: './footer.scss',
})
export class Footer {
  /** Build-time constant from scripts/gen-version.mjs — never changes at runtime. */
  protected readonly version = VERSION;

  /** API version, read live from /health so the footer reflects the deployed backend. */
  protected readonly health = httpResource<Health>(() => `${environment.apiUrl}/health`);
}
