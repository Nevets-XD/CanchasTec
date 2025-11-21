import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';

interface LoginResponse {
  message: string;
  user: {
    id: number;
    nombre: string;
    email: string;
    tipo_usuario: string;
  };
}

interface RegisterResponse {
  message: string;
  id: number;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private apiUrl = 'http://localhost:5000/api';
  private currentUserSubject: BehaviorSubject<any>;
  public currentUser: Observable<any>;

  constructor(private http: HttpClient) {
    const storedUser = localStorage.getItem('currentUser');
    this.currentUserSubject = new BehaviorSubject<any>(
      storedUser ? JSON.parse(storedUser) : null
    );
    this.currentUser = this.currentUserSubject.asObservable();
  }

  public get currentUserValue() {
    return this.currentUserSubject.value;
  }

  login(email: string, password: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${this.apiUrl}/Login`, {
        email,
        password,
      })
      .pipe(
        tap((response) => {
          if (response.user) {
            localStorage.setItem('currentUser', JSON.stringify(response.user));
            this.currentUserSubject.next(response.user);
            console.log('💾 Usuario guardado en localStorage:', response.user);
          }
        })
      );
  }

  register(
    nombre: string,
    email: string,
    password: string,
    tipo_usuario: string
  ): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(`${this.apiUrl}/Register`, {
      nombre,
      email,
      password,
      tipo_usuario,
    });
  }

  logout(): void {
    localStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
  }

  isLoggedIn(): boolean {
    return !!this.currentUserValue;
  }

  isAdmin(): boolean {
    const user = this.currentUserValue;
    return user && user.tipo_usuario.toLowerCase() === 'administrador';
  }

  isUsuario(): boolean {
    const user = this.currentUserValue;
    return user && user.tipo_usuario.toLowerCase() === 'usuario';
  }
}