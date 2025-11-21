import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink],
  templateUrl: './login.html',
  styleUrls: ['./login.css'],
})
export class LoginComponent {
  email: string = '';
  password: string = '';
  rememberMe: boolean = false;
  errorMessage: string = '';
  isLoading: boolean = false;

  constructor(private authService: AuthService, private router: Router) {}

  onLogin(): void {
    this.errorMessage = '';

    if (!this.email || !this.password) {
      this.errorMessage = 'Por favor completa todos los campos';
      return;
    }

    this.isLoading = true;

    this.authService.login(this.email, this.password).subscribe({
      next: (response) => {
        console.log('✅ Login exitoso:', response);
        console.log('📋 Tipo de usuario recibido:', response.user.tipo_usuario);
        
        this.isLoading = false;
        alert('¡Bienvenido ' + response.user.nombre + '!');

        // Convertir a minúsculas para comparar
        const tipo = response.user.tipo_usuario.toLowerCase();
        console.log('🔍 Tipo normalizado:', tipo);

        // VALIDACIÓN DEL TIPO DE USUARIO (con los valores correctos)
        if (tipo === 'administrador') {
          console.log('➡️ Redirigiendo a /admin');
          this.router.navigate(['/admin']);
        } else if (tipo === 'usuario') {
          console.log('➡️ Redirigiendo a /client');
          this.router.navigate(['/client']);
        } else {
          console.log('⚠️ Tipo desconocido, redirigiendo a home');
          this.router.navigate(['/']);
        }
      },

      error: (error) => {
        console.error('❌ Error en login:', error);
        this.isLoading = false;
        this.errorMessage = error.error?.message || 'Error al iniciar sesión';
      },
    });
  }
}