import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'emaily';
  constructor(private router: Router) { }

  goRegister(): void {
    this.router.navigate(['/register']);
  }

  goLogin(): void {
    this.router.navigate(['/login']);
  }
}
