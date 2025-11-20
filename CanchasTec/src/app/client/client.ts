import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-client',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './client.html',
  styleUrls: ['./client.css']
})
export class ClientComponent implements OnInit {
  currentUser: any = null;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.currentUserValue;
    
    // Verificar que sea usuario regular
    if (!this.currentUser || this.currentUser.tipo_usuario.toLowerCase() !== 'usuario') {
      alert('Acceso denegado.');
      this.router.navigate(['/']);
    }
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/Login']);
  }
}