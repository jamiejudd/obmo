!function(r){"use strict";function t(r,t,n,e){r[t]=n>>24&255,r[t+1]=n>>16&255,r[t+2]=n>>8&255,r[t+3]=255&n,r[t+4]=e>>24&255,r[t+5]=e>>16&255,r[t+6]=e>>8&255,r[t+7]=255&e}function n(r,t,n,e,o){var i,h=0;for(i=0;i<o;i++)h|=r[t+i]^n[e+i];return(1&h-1>>>8)-1}function e(r,t,e,o){return n(r,t,e,o,16)}function o(r,t,e,o){return n(r,t,e,o,32)}function i(r,t,n,e){for(var o,i=255&e[0]|(255&e[1])<<8|(255&e[2])<<16|(255&e[3])<<24,h=255&n[0]|(255&n[1])<<8|(255&n[2])<<16|(255&n[3])<<24,a=255&n[4]|(255&n[5])<<8|(255&n[6])<<16|(255&n[7])<<24,f=255&n[8]|(255&n[9])<<8|(255&n[10])<<16|(255&n[11])<<24,s=255&n[12]|(255&n[13])<<8|(255&n[14])<<16|(255&n[15])<<24,u=255&e[4]|(255&e[5])<<8|(255&e[6])<<16|(255&e[7])<<24,c=255&t[0]|(255&t[1])<<8|(255&t[2])<<16|(255&t[3])<<24,y=255&t[4]|(255&t[5])<<8|(255&t[6])<<16|(255&t[7])<<24,l=255&t[8]|(255&t[9])<<8|(255&t[10])<<16|(255&t[11])<<24,w=255&t[12]|(255&t[13])<<8|(255&t[14])<<16|(255&t[15])<<24,v=255&e[8]|(255&e[9])<<8|(255&e[10])<<16|(255&e[11])<<24,p=255&n[16]|(255&n[17])<<8|(255&n[18])<<16|(255&n[19])<<24,b=255&n[20]|(255&n[21])<<8|(255&n[22])<<16|(255&n[23])<<24,g=255&n[24]|(255&n[25])<<8|(255&n[26])<<16|(255&n[27])<<24,_=255&n[28]|(255&n[29])<<8|(255&n[30])<<16|(255&n[31])<<24,A=255&e[12]|(255&e[13])<<8|(255&e[14])<<16|(255&e[15])<<24,U=i,d=h,E=a,x=f,M=s,m=u,B=c,S=y,K=l,Y=w,k=v,T=p,L=b,z=g,R=_,P=A,N=0;N<20;N+=2)o=U+L|0,M^=o<<7|o>>>25,o=M+U|0,K^=o<<9|o>>>23,o=K+M|0,L^=o<<13|o>>>19,o=L+K|0,U^=o<<18|o>>>14,o=m+d|0,Y^=o<<7|o>>>25,o=Y+m|0,z^=o<<9|o>>>23,o=z+Y|0,d^=o<<13|o>>>19,o=d+z|0,m^=o<<18|o>>>14,o=k+B|0,R^=o<<7|o>>>25,o=R+k|0,E^=o<<9|o>>>23,o=E+R|0,B^=o<<13|o>>>19,o=B+E|0,k^=o<<18|o>>>14,o=P+T|0,x^=o<<7|o>>>25,o=x+P|0,S^=o<<9|o>>>23,o=S+x|0,T^=o<<13|o>>>19,o=T+S|0,P^=o<<18|o>>>14,o=U+x|0,d^=o<<7|o>>>25,o=d+U|0,E^=o<<9|o>>>23,o=E+d|0,x^=o<<13|o>>>19,o=x+E|0,U^=o<<18|o>>>14,o=m+M|0,B^=o<<7|o>>>25,o=B+m|0,S^=o<<9|o>>>23,o=S+B|0,M^=o<<13|o>>>19,o=M+S|0,m^=o<<18|o>>>14,o=k+Y|0,T^=o<<7|o>>>25,o=T+k|0,K^=o<<9|o>>>23,o=K+T|0,Y^=o<<13|o>>>19,o=Y+K|0,k^=o<<18|o>>>14,o=P+R|0,L^=o<<7|o>>>25,o=L+P|0,z^=o<<9|o>>>23,o=z+L|0,R^=o<<13|o>>>19,o=R+z|0,P^=o<<18|o>>>14;U=U+i|0,d=d+h|0,E=E+a|0,x=x+f|0,M=M+s|0,m=m+u|0,B=B+c|0,S=S+y|0,K=K+l|0,Y=Y+w|0,k=k+v|0,T=T+p|0,L=L+b|0,z=z+g|0,R=R+_|0,P=P+A|0,r[0]=U>>>0&255,r[1]=U>>>8&255,r[2]=U>>>16&255,r[3]=U>>>24&255,r[4]=d>>>0&255,r[5]=d>>>8&255,r[6]=d>>>16&255,r[7]=d>>>24&255,r[8]=E>>>0&255,r[9]=E>>>8&255,r[10]=E>>>16&255,r[11]=E>>>24&255,r[12]=x>>>0&255,r[13]=x>>>8&255,r[14]=x>>>16&255,r[15]=x>>>24&255,r[16]=M>>>0&255,r[17]=M>>>8&255,r[18]=M>>>16&255,r[19]=M>>>24&255,r[20]=m>>>0&255,r[21]=m>>>8&255,r[22]=m>>>16&255,r[23]=m>>>24&255,r[24]=B>>>0&255,r[25]=B>>>8&255,r[26]=B>>>16&255,r[27]=B>>>24&255,r[28]=S>>>0&255,r[29]=S>>>8&255,r[30]=S>>>16&255,r[31]=S>>>24&255,r[32]=K>>>0&255,r[33]=K>>>8&255,r[34]=K>>>16&255,r[35]=K>>>24&255,r[36]=Y>>>0&255,r[37]=Y>>>8&255,r[38]=Y>>>16&255,r[39]=Y>>>24&255,r[40]=k>>>0&255,r[41]=k>>>8&255,r[42]=k>>>16&255,r[43]=k>>>24&255,r[44]=T>>>0&255,r[45]=T>>>8&255,r[46]=T>>>16&255,r[47]=T>>>24&255,r[48]=L>>>0&255,r[49]=L>>>8&255,r[50]=L>>>16&255,r[51]=L>>>24&255,r[52]=z>>>0&255,r[53]=z>>>8&255,r[54]=z>>>16&255,r[55]=z>>>24&255,r[56]=R>>>0&255,r[57]=R>>>8&255,r[58]=R>>>16&255,r[59]=R>>>24&255,r[60]=P>>>0&255,r[61]=P>>>8&255,r[62]=P>>>16&255,r[63]=P>>>24&255}function h(r,t,n,e){for(var o,i=255&e[0]|(255&e[1])<<8|(255&e[2])<<16|(255&e[3])<<24,h=255&n[0]|(255&n[1])<<8|(255&n[2])<<16|(255&n[3])<<24,a=255&n[4]|(255&n[5])<<8|(255&n[6])<<16|(255&n[7])<<24,f=255&n[8]|(255&n[9])<<8|(255&n[10])<<16|(255&n[11])<<24,s=255&n[12]|(255&n[13])<<8|(255&n[14])<<16|(255&n[15])<<24,u=255&e[4]|(255&e[5])<<8|(255&e[6])<<16|(255&e[7])<<24,c=255&t[0]|(255&t[1])<<8|(255&t[2])<<16|(255&t[3])<<24,y=255&t[4]|(255&t[5])<<8|(255&t[6])<<16|(255&t[7])<<24,l=255&t[8]|(255&t[9])<<8|(255&t[10])<<16|(255&t[11])<<24,w=255&t[12]|(255&t[13])<<8|(255&t[14])<<16|(255&t[15])<<24,v=255&e[8]|(255&e[9])<<8|(255&e[10])<<16|(255&e[11])<<24,p=255&n[16]|(255&n[17])<<8|(255&n[18])<<16|(255&n[19])<<24,b=255&n[20]|(255&n[21])<<8|(255&n[22])<<16|(255&n[23])<<24,g=255&n[24]|(255&n[25])<<8|(255&n[26])<<16|(255&n[27])<<24,_=255&n[28]|(255&n[29])<<8|(255&n[30])<<16|(255&n[31])<<24,A=255&e[12]|(255&e[13])<<8|(255&e[14])<<16|(255&e[15])<<24,U=i,d=h,E=a,x=f,M=s,m=u,B=c,S=y,K=l,Y=w,k=v,T=p,L=b,z=g,R=_,P=A,N=0;N<20;N+=2)o=U+L|0,M^=o<<7|o>>>25,o=M+U|0,K^=o<<9|o>>>23,o=K+M|0,L^=o<<13|o>>>19,o=L+K|0,U^=o<<18|o>>>14,o=m+d|0,Y^=o<<7|o>>>25,o=Y+m|0,z^=o<<9|o>>>23,o=z+Y|0,d^=o<<13|o>>>19,o=d+z|0,m^=o<<18|o>>>14,o=k+B|0,R^=o<<7|o>>>25,o=R+k|0,E^=o<<9|o>>>23,o=E+R|0,B^=o<<13|o>>>19,o=B+E|0,k^=o<<18|o>>>14,o=P+T|0,x^=o<<7|o>>>25,o=x+P|0,S^=o<<9|o>>>23,o=S+x|0,T^=o<<13|o>>>19,o=T+S|0,P^=o<<18|o>>>14,o=U+x|0,d^=o<<7|o>>>25,o=d+U|0,E^=o<<9|o>>>23,o=E+d|0,x^=o<<13|o>>>19,o=x+E|0,U^=o<<18|o>>>14,o=m+M|0,B^=o<<7|o>>>25,o=B+m|0,S^=o<<9|o>>>23,o=S+B|0,M^=o<<13|o>>>19,o=M+S|0,m^=o<<18|o>>>14,o=k+Y|0,T^=o<<7|o>>>25,o=T+k|0,K^=o<<9|o>>>23,o=K+T|0,Y^=o<<13|o>>>19,o=Y+K|0,k^=o<<18|o>>>14,o=P+R|0,L^=o<<7|o>>>25,o=L+P|0,z^=o<<9|o>>>23,o=z+L|0,R^=o<<13|o>>>19,o=R+z|0,P^=o<<18|o>>>14;r[0]=U>>>0&255,r[1]=U>>>8&255,r[2]=U>>>16&255,r[3]=U>>>24&255,r[4]=m>>>0&255,r[5]=m>>>8&255,r[6]=m>>>16&255,r[7]=m>>>24&255,r[8]=k>>>0&255,r[9]=k>>>8&255,r[10]=k>>>16&255,r[11]=k>>>24&255,r[12]=P>>>0&255,r[13]=P>>>8&255,r[14]=P>>>16&255,r[15]=P>>>24&255,r[16]=B>>>0&255,r[17]=B>>>8&255,r[18]=B>>>16&255,r[19]=B>>>24&255,r[20]=S>>>0&255,r[21]=S>>>8&255,r[22]=S>>>16&255,r[23]=S>>>24&255,r[24]=K>>>0&255,r[25]=K>>>8&255,r[26]=K>>>16&255,r[27]=K>>>24&255,r[28]=Y>>>0&255,r[29]=Y>>>8&255,r[30]=Y>>>16&255,r[31]=Y>>>24&255}function a(r,t,n,e){i(r,t,n,e)}function f(r,t,n,e){h(r,t,n,e)}function s(r,t,n,e,o,i,h){var f,s,u=new Uint8Array(16),c=new Uint8Array(64);for(s=0;s<16;s++)u[s]=0;for(s=0;s<8;s++)u[s]=i[s];for(;o>=64;){for(a(c,u,h,cr),s=0;s<64;s++)r[t+s]=n[e+s]^c[s];for(f=1,s=8;s<16;s++)f=f+(255&u[s])|0,u[s]=255&f,f>>>=8;o-=64,t+=64,e+=64}if(o>0)for(a(c,u,h,cr),s=0;s<o;s++)r[t+s]=n[e+s]^c[s];return 0}function u(r,t,n,e,o){var i,h,f=new Uint8Array(16),s=new Uint8Array(64);for(h=0;h<16;h++)f[h]=0;for(h=0;h<8;h++)f[h]=e[h];for(;n>=64;){for(a(s,f,o,cr),h=0;h<64;h++)r[t+h]=s[h];for(i=1,h=8;h<16;h++)i=i+(255&f[h])|0,f[h]=255&i,i>>>=8;n-=64,t+=64}if(n>0)for(a(s,f,o,cr),h=0;h<n;h++)r[t+h]=s[h];return 0}function c(r,t,n,e,o){var i=new Uint8Array(32);f(i,e,o,cr);for(var h=new Uint8Array(8),a=0;a<8;a++)h[a]=e[a+16];return u(r,t,n,h,i)}function y(r,t,n,e,o,i,h){var a=new Uint8Array(32);f(a,i,h,cr);for(var u=new Uint8Array(8),c=0;c<8;c++)u[c]=i[c+16];return s(r,t,n,e,o,u,a)}function l(r,t,n,e,o,i){var h=new yr(i);return h.update(n,e,o),h.finish(r,t),0}function w(r,t,n,o,i,h){var a=new Uint8Array(16);return l(a,0,n,o,i,h),e(r,t,a,0)}function v(r,t,n,e,o){var i;if(n<32)return-1;for(y(r,0,t,0,n,e,o),l(r,16,r,32,n-32,r),i=0;i<16;i++)r[i]=0;return 0}function p(r,t,n,e,o){var i,h=new Uint8Array(32);if(n<32)return-1;if(c(h,0,32,e,o),0!==w(t,16,t,32,n-32,h))return-1;for(y(r,0,t,0,n,e,o),i=0;i<32;i++)r[i]=0;return 0}function b(r,t){var n;for(n=0;n<16;n++)r[n]=0|t[n]}function g(r){var t,n,e=1;for(t=0;t<16;t++)n=r[t]+e+65535,e=Math.floor(n/65536),r[t]=n-65536*e;r[0]+=e-1+37*(e-1)}function _(r,t,n){for(var e,o=~(n-1),i=0;i<16;i++)e=o&(r[i]^t[i]),r[i]^=e,t[i]^=e}function A(r,t){var n,e,o,i=$(),h=$();for(n=0;n<16;n++)h[n]=t[n];for(g(h),g(h),g(h),e=0;e<2;e++){for(i[0]=h[0]-65517,n=1;n<15;n++)i[n]=h[n]-65535-(i[n-1]>>16&1),i[n-1]&=65535;i[15]=h[15]-32767-(i[14]>>16&1),o=i[15]>>16&1,i[14]&=65535,_(h,i,1-o)}for(n=0;n<16;n++)r[2*n]=255&h[n],r[2*n+1]=h[n]>>8}function U(r,t){var n=new Uint8Array(32),e=new Uint8Array(32);return A(n,r),A(e,t),o(n,0,e,0)}function d(r){var t=new Uint8Array(32);return A(t,r),1&t[0]}function E(r,t){var n;for(n=0;n<16;n++)r[n]=t[2*n]+(t[2*n+1]<<8);r[15]&=32767}function x(r,t,n){for(var e=0;e<16;e++)r[e]=t[e]+n[e]}function M(r,t,n){for(var e=0;e<16;e++)r[e]=t[e]-n[e]}function m(r,t,n){var e,o,i=0,h=0,a=0,f=0,s=0,u=0,c=0,y=0,l=0,w=0,v=0,p=0,b=0,g=0,_=0,A=0,U=0,d=0,E=0,x=0,M=0,m=0,B=0,S=0,K=0,Y=0,k=0,T=0,L=0,z=0,R=0,P=n[0],N=n[1],O=n[2],C=n[3],F=n[4],I=n[5],G=n[6],Z=n[7],q=n[8],V=n[9],X=n[10],D=n[11],j=n[12],H=n[13],J=n[14],Q=n[15];e=t[0],i+=e*P,h+=e*N,a+=e*O,f+=e*C,s+=e*F,u+=e*I,c+=e*G,y+=e*Z,l+=e*q,w+=e*V,v+=e*X,p+=e*D,b+=e*j,g+=e*H,_+=e*J,A+=e*Q,e=t[1],h+=e*P,a+=e*N,f+=e*O,s+=e*C,u+=e*F,c+=e*I,y+=e*G,l+=e*Z,w+=e*q,v+=e*V,p+=e*X,b+=e*D,g+=e*j,_+=e*H,A+=e*J,U+=e*Q,e=t[2],a+=e*P,f+=e*N,s+=e*O,u+=e*C,c+=e*F,y+=e*I,l+=e*G,w+=e*Z,v+=e*q,p+=e*V,b+=e*X,g+=e*D,_+=e*j,A+=e*H,U+=e*J,d+=e*Q,e=t[3],f+=e*P,s+=e*N,u+=e*O,c+=e*C,y+=e*F,l+=e*I,w+=e*G,v+=e*Z,p+=e*q,b+=e*V,g+=e*X,_+=e*D,A+=e*j,U+=e*H,d+=e*J,E+=e*Q,e=t[4],s+=e*P,u+=e*N,c+=e*O,y+=e*C,l+=e*F,w+=e*I,v+=e*G,p+=e*Z,b+=e*q,g+=e*V,_+=e*X,A+=e*D,U+=e*j,d+=e*H,E+=e*J,x+=e*Q,e=t[5],u+=e*P,c+=e*N,y+=e*O,l+=e*C,w+=e*F,v+=e*I,p+=e*G,b+=e*Z,g+=e*q,_+=e*V,A+=e*X,U+=e*D,d+=e*j,E+=e*H,x+=e*J,M+=e*Q,e=t[6],c+=e*P,y+=e*N,l+=e*O,w+=e*C,v+=e*F,p+=e*I,b+=e*G,g+=e*Z,_+=e*q,A+=e*V,U+=e*X,d+=e*D,E+=e*j,x+=e*H,M+=e*J,m+=e*Q,e=t[7],y+=e*P,l+=e*N,w+=e*O,v+=e*C,p+=e*F,b+=e*I,g+=e*G,_+=e*Z,A+=e*q,U+=e*V,d+=e*X,E+=e*D,x+=e*j,M+=e*H,m+=e*J,B+=e*Q,e=t[8],l+=e*P,w+=e*N,v+=e*O,p+=e*C,b+=e*F,g+=e*I,_+=e*G,A+=e*Z,U+=e*q,d+=e*V,E+=e*X,x+=e*D,M+=e*j,m+=e*H,B+=e*J,S+=e*Q,e=t[9],w+=e*P,v+=e*N,p+=e*O,b+=e*C,g+=e*F,_+=e*I,A+=e*G,U+=e*Z,d+=e*q,E+=e*V,x+=e*X,M+=e*D,m+=e*j,B+=e*H,S+=e*J,K+=e*Q,e=t[10],v+=e*P,p+=e*N,b+=e*O,g+=e*C,_+=e*F,A+=e*I,U+=e*G,d+=e*Z,E+=e*q,x+=e*V,M+=e*X,m+=e*D,B+=e*j,S+=e*H,K+=e*J,Y+=e*Q,e=t[11],p+=e*P,b+=e*N,g+=e*O,_+=e*C,A+=e*F,U+=e*I,d+=e*G,E+=e*Z,x+=e*q,M+=e*V,m+=e*X,B+=e*D;S+=e*j;K+=e*H,Y+=e*J,k+=e*Q,e=t[12],b+=e*P,g+=e*N,_+=e*O,A+=e*C,U+=e*F,d+=e*I,E+=e*G,x+=e*Z,M+=e*q,m+=e*V,B+=e*X,S+=e*D,K+=e*j,Y+=e*H,k+=e*J,T+=e*Q,e=t[13],g+=e*P,_+=e*N,A+=e*O,U+=e*C,d+=e*F,E+=e*I,x+=e*G,M+=e*Z,m+=e*q,B+=e*V,S+=e*X,K+=e*D,Y+=e*j,k+=e*H,T+=e*J,L+=e*Q,e=t[14],_+=e*P,A+=e*N,U+=e*O,d+=e*C,E+=e*F,x+=e*I,M+=e*G,m+=e*Z,B+=e*q,S+=e*V,K+=e*X,Y+=e*D,k+=e*j,T+=e*H,L+=e*J,z+=e*Q,e=t[15],A+=e*P,U+=e*N,d+=e*O,E+=e*C,x+=e*F,M+=e*I,m+=e*G,B+=e*Z,S+=e*q,K+=e*V,Y+=e*X,k+=e*D,T+=e*j,L+=e*H,z+=e*J,R+=e*Q,i+=38*U,h+=38*d,a+=38*E,f+=38*x,s+=38*M,u+=38*m,c+=38*B,y+=38*S,l+=38*K,w+=38*Y,v+=38*k,p+=38*T,b+=38*L,g+=38*z,_+=38*R,o=1,e=i+o+65535,o=Math.floor(e/65536),i=e-65536*o,e=h+o+65535,o=Math.floor(e/65536),h=e-65536*o,e=a+o+65535,o=Math.floor(e/65536),a=e-65536*o,e=f+o+65535,o=Math.floor(e/65536),f=e-65536*o,e=s+o+65535,o=Math.floor(e/65536),s=e-65536*o,e=u+o+65535,o=Math.floor(e/65536),u=e-65536*o,e=c+o+65535,o=Math.floor(e/65536),c=e-65536*o,e=y+o+65535,o=Math.floor(e/65536),y=e-65536*o,e=l+o+65535,o=Math.floor(e/65536),l=e-65536*o,e=w+o+65535,o=Math.floor(e/65536),w=e-65536*o,e=v+o+65535,o=Math.floor(e/65536),v=e-65536*o,e=p+o+65535,o=Math.floor(e/65536),p=e-65536*o,e=b+o+65535,o=Math.floor(e/65536),b=e-65536*o,e=g+o+65535,o=Math.floor(e/65536),g=e-65536*o,e=_+o+65535,o=Math.floor(e/65536),_=e-65536*o,e=A+o+65535,o=Math.floor(e/65536),A=e-65536*o,i+=o-1+37*(o-1),o=1,e=i+o+65535,o=Math.floor(e/65536),i=e-65536*o,e=h+o+65535,o=Math.floor(e/65536),h=e-65536*o,e=a+o+65535,o=Math.floor(e/65536),a=e-65536*o,e=f+o+65535,o=Math.floor(e/65536),f=e-65536*o,e=s+o+65535,o=Math.floor(e/65536),s=e-65536*o,e=u+o+65535,o=Math.floor(e/65536),u=e-65536*o,e=c+o+65535,o=Math.floor(e/65536),c=e-65536*o,e=y+o+65535,o=Math.floor(e/65536),y=e-65536*o,e=l+o+65535,o=Math.floor(e/65536),l=e-65536*o,e=w+o+65535,o=Math.floor(e/65536),w=e-65536*o,e=v+o+65535,o=Math.floor(e/65536),v=e-65536*o,e=p+o+65535,o=Math.floor(e/65536),p=e-65536*o,e=b+o+65535,o=Math.floor(e/65536),b=e-65536*o,e=g+o+65535,o=Math.floor(e/65536),g=e-65536*o,e=_+o+65535,o=Math.floor(e/65536),_=e-65536*o,e=A+o+65535,o=Math.floor(e/65536),A=e-65536*o,i+=o-1+37*(o-1),r[0]=i,r[1]=h,r[2]=a,r[3]=f,r[4]=s,r[5]=u,r[6]=c,r[7]=y,r[8]=l,r[9]=w,r[10]=v,r[11]=p,r[12]=b,r[13]=g;r[14]=_;r[15]=A}function B(r,t){m(r,t,t)}function S(r,t){var n,e=$();for(n=0;n<16;n++)e[n]=t[n];for(n=253;n>=0;n--)B(e,e),2!==n&&4!==n&&m(e,e,t);for(n=0;n<16;n++)r[n]=e[n]}function K(r,t){var n,e=$();for(n=0;n<16;n++)e[n]=t[n];for(n=250;n>=0;n--)B(e,e),1!==n&&m(e,e,t);for(n=0;n<16;n++)r[n]=e[n]}function Y(r,t,n){var e,o,i=new Uint8Array(32),h=new Float64Array(80),a=$(),f=$(),s=$(),u=$(),c=$(),y=$();for(o=0;o<31;o++)i[o]=t[o];for(i[31]=127&t[31]|64,i[0]&=248,E(h,n),o=0;o<16;o++)f[o]=h[o],u[o]=a[o]=s[o]=0;for(a[0]=u[0]=1,o=254;o>=0;--o)e=i[o>>>3]>>>(7&o)&1,_(a,f,e),_(s,u,e),x(c,a,s),M(a,a,s),x(s,f,u),M(f,f,u),B(u,c),B(y,a),m(a,s,a),m(s,f,c),x(c,a,s),M(a,a,s),B(f,a),M(s,u,y),m(a,s,ir),x(a,a,u),m(s,s,a),m(a,u,y),m(u,f,h),B(f,c),_(a,f,e),_(s,u,e);for(o=0;o<16;o++)h[o+16]=a[o],h[o+32]=s[o],h[o+48]=f[o],h[o+64]=u[o];var l=h.subarray(32),w=h.subarray(16);return S(l,l),m(w,w,l),A(r,w),0}function k(r,t){return Y(r,t,nr)}function T(r,t){return rr(t,32),k(r,t)}function L(r,t,n){var e=new Uint8Array(32);return Y(e,n,t),f(r,tr,e,cr)}function z(r,t,n,e,o,i){var h=new Uint8Array(32);return L(h,o,i),lr(r,t,n,e,h)}function R(r,t,n,e,o,i){var h=new Uint8Array(32);return L(h,o,i),wr(r,t,n,e,h)}function P(r,t,n,e){for(var o,i,h,a,f,s,u,c,y,l,w,v,p,b,g,_,A,U,d,E,x,M,m,B,S,K,Y=new Int32Array(16),k=new Int32Array(16),T=r[0],L=r[1],z=r[2],R=r[3],P=r[4],N=r[5],O=r[6],C=r[7],F=t[0],I=t[1],G=t[2],Z=t[3],q=t[4],V=t[5],X=t[6],D=t[7],j=0;e>=128;){for(d=0;d<16;d++)E=8*d+j,Y[d]=n[E+0]<<24|n[E+1]<<16|n[E+2]<<8|n[E+3],k[d]=n[E+4]<<24|n[E+5]<<16|n[E+6]<<8|n[E+7];for(d=0;d<80;d++)if(o=T,i=L,h=z,a=R,f=P,s=N,u=O,c=C,y=F,l=I,w=G,v=Z,p=q,b=V,g=X,_=D,x=C,M=D,m=65535&M,B=M>>>16,S=65535&x,K=x>>>16,x=(P>>>14|q<<18)^(P>>>18|q<<14)^(q>>>9|P<<23),M=(q>>>14|P<<18)^(q>>>18|P<<14)^(P>>>9|q<<23),m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,x=P&N^~P&O,M=q&V^~q&X,m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,x=vr[2*d],M=vr[2*d+1],m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,x=Y[d%16],M=k[d%16],m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,B+=m>>>16,S+=B>>>16,K+=S>>>16,A=65535&S|K<<16,U=65535&m|B<<16,x=A,M=U,m=65535&M,B=M>>>16,S=65535&x,K=x>>>16,x=(T>>>28|F<<4)^(F>>>2|T<<30)^(F>>>7|T<<25),M=(F>>>28|T<<4)^(T>>>2|F<<30)^(T>>>7|F<<25),m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,x=T&L^T&z^L&z,M=F&I^F&G^I&G,m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,B+=m>>>16,S+=B>>>16,K+=S>>>16,c=65535&S|K<<16,_=65535&m|B<<16,x=a,M=v,m=65535&M,B=M>>>16,S=65535&x,K=x>>>16,x=A,M=U,m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,B+=m>>>16,S+=B>>>16,K+=S>>>16,a=65535&S|K<<16,v=65535&m|B<<16,L=o,z=i,R=h,P=a,N=f,O=s,C=u,T=c,I=y,G=l,Z=w,q=v,V=p,X=b,D=g,F=_,d%16===15)for(E=0;E<16;E++)x=Y[E],M=k[E],m=65535&M,B=M>>>16,S=65535&x,K=x>>>16,x=Y[(E+9)%16],M=k[(E+9)%16],m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,A=Y[(E+1)%16],U=k[(E+1)%16],x=(A>>>1|U<<31)^(A>>>8|U<<24)^A>>>7,M=(U>>>1|A<<31)^(U>>>8|A<<24)^(U>>>7|A<<25),m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,A=Y[(E+14)%16],U=k[(E+14)%16],x=(A>>>19|U<<13)^(U>>>29|A<<3)^A>>>6,M=(U>>>19|A<<13)^(A>>>29|U<<3)^(U>>>6|A<<26),m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,B+=m>>>16,S+=B>>>16,K+=S>>>16,Y[E]=65535&S|K<<16,k[E]=65535&m|B<<16;x=T,M=F,m=65535&M,B=M>>>16,S=65535&x,K=x>>>16,x=r[0],M=t[0],m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,B+=m>>>16,S+=B>>>16,K+=S>>>16,r[0]=T=65535&S|K<<16,t[0]=F=65535&m|B<<16,x=L,M=I,m=65535&M,B=M>>>16,S=65535&x,K=x>>>16,x=r[1],M=t[1],m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,B+=m>>>16,S+=B>>>16,K+=S>>>16,r[1]=L=65535&S|K<<16,t[1]=I=65535&m|B<<16,x=z,M=G,m=65535&M,B=M>>>16,S=65535&x,K=x>>>16,x=r[2],M=t[2],m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,B+=m>>>16,S+=B>>>16,K+=S>>>16,r[2]=z=65535&S|K<<16,t[2]=G=65535&m|B<<16,x=R,M=Z,m=65535&M,B=M>>>16,S=65535&x,K=x>>>16,x=r[3],M=t[3],m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,B+=m>>>16,S+=B>>>16,K+=S>>>16,r[3]=R=65535&S|K<<16,t[3]=Z=65535&m|B<<16,x=P,M=q,m=65535&M,B=M>>>16,S=65535&x,K=x>>>16,x=r[4],M=t[4],m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,B+=m>>>16,S+=B>>>16,K+=S>>>16,r[4]=P=65535&S|K<<16,t[4]=q=65535&m|B<<16,x=N,M=V,m=65535&M,B=M>>>16,S=65535&x,K=x>>>16,x=r[5],M=t[5],m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,B+=m>>>16,S+=B>>>16,K+=S>>>16,r[5]=N=65535&S|K<<16,t[5]=V=65535&m|B<<16,x=O,M=X,m=65535&M,B=M>>>16,S=65535&x,K=x>>>16,x=r[6],M=t[6],m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,B+=m>>>16,S+=B>>>16,K+=S>>>16,r[6]=O=65535&S|K<<16,t[6]=X=65535&m|B<<16,x=C,M=D,m=65535&M,B=M>>>16,S=65535&x,K=x>>>16,x=r[7],M=t[7],m+=65535&M,B+=M>>>16,S+=65535&x,K+=x>>>16,B+=m>>>16,S+=B>>>16,K+=S>>>16,r[7]=C=65535&S|K<<16,t[7]=D=65535&m|B<<16,j+=128,e-=128}return e}function N(r,n,e){var o,i=new Int32Array(8),h=new Int32Array(8),a=new Uint8Array(256),f=e;for(i[0]=1779033703,i[1]=3144134277,i[2]=1013904242,i[3]=2773480762,i[4]=1359893119,i[5]=2600822924,i[6]=528734635,i[7]=1541459225,h[0]=4089235720,h[1]=2227873595,h[2]=4271175723,h[3]=1595750129,h[4]=2917565137,h[5]=725511199,h[6]=4215389547,h[7]=327033209,P(i,h,n,e),e%=128,o=0;o<e;o++)a[o]=n[f-e+o];for(a[e]=128,e=256-128*(e<112?1:0),a[e-9]=0,t(a,e-8,f/536870912|0,f<<3),P(i,h,a,e),o=0;o<8;o++)t(r,8*o,i[o],h[o]);return 0}function O(r,t){var n=$(),e=$(),o=$(),i=$(),h=$(),a=$(),f=$(),s=$(),u=$();M(n,r[1],r[0]),M(u,t[1],t[0]),m(n,n,u),x(e,r[0],r[1]),x(u,t[0],t[1]),m(e,e,u),m(o,r[3],t[3]),m(o,o,ar),m(i,r[2],t[2]),x(i,i,i),M(h,e,n),M(a,i,o),x(f,i,o),x(s,e,n),m(r[0],h,a),m(r[1],s,f),m(r[2],f,a),m(r[3],h,s)}function C(r,t,n){var e;for(e=0;e<4;e++)_(r[e],t[e],n)}function F(r,t){var n=$(),e=$(),o=$();S(o,t[2]),m(n,t[0],o),m(e,t[1],o),A(r,e),r[31]^=d(n)<<7}function I(r,t,n){var e,o;for(b(r[0],er),b(r[1],or),b(r[2],or),b(r[3],er),o=255;o>=0;--o)e=n[o/8|0]>>(7&o)&1,C(r,t,e),O(t,r),O(r,r),C(r,t,e)}function G(r,t){var n=[$(),$(),$(),$()];b(n[0],fr),b(n[1],sr),b(n[2],or),m(n[3],fr,sr),I(r,n,t)}function Z(r,t,n){var e,o=new Uint8Array(64),i=[$(),$(),$(),$()];for(n||rr(t,32),N(o,t,32),o[0]&=248,o[31]&=127,o[31]|=64,G(i,o),F(r,i),e=0;e<32;e++)t[e+32]=r[e];return 0}function q(r,t){var n,e,o,i;for(e=63;e>=32;--e){for(n=0,o=e-32,i=e-12;o<i;++o)t[o]+=n-16*t[e]*pr[o-(e-32)],n=t[o]+128>>8,t[o]-=256*n;t[o]+=n,t[e]=0}for(n=0,o=0;o<32;o++)t[o]+=n-(t[31]>>4)*pr[o],n=t[o]>>8,t[o]&=255;for(o=0;o<32;o++)t[o]-=n*pr[o];for(e=0;e<32;e++)t[e+1]+=t[e]>>8,r[e]=255&t[e]}function V(r){var t,n=new Float64Array(64);for(t=0;t<64;t++)n[t]=r[t];for(t=0;t<64;t++)r[t]=0;q(r,n)}function X(r,t,n,e){var o,i,h=new Uint8Array(64),a=new Uint8Array(64),f=new Uint8Array(64),s=new Float64Array(64),u=[$(),$(),$(),$()];N(h,e,32),h[0]&=248,h[31]&=127,h[31]|=64;var c=n+64;for(o=0;o<n;o++)r[64+o]=t[o];for(o=0;o<32;o++)r[32+o]=h[32+o];for(N(f,r.subarray(32),n+32),V(f),G(u,f),F(r,u),o=32;o<64;o++)r[o]=e[o];for(N(a,r,n+64),V(a),o=0;o<64;o++)s[o]=0;for(o=0;o<32;o++)s[o]=f[o];for(o=0;o<32;o++)for(i=0;i<32;i++)s[o+i]+=a[o]*h[i];return q(r.subarray(32),s),c}function D(r,t){var n=$(),e=$(),o=$(),i=$(),h=$(),a=$(),f=$();return b(r[2],or),E(r[1],t),B(o,r[1]),m(i,o,hr),M(o,o,r[2]),x(i,r[2],i),B(h,i),B(a,h),m(f,a,h),m(n,f,o),m(n,n,i),K(n,n),m(n,n,o),m(n,n,i),m(n,n,i),m(r[0],n,i),B(e,r[0]),m(e,e,i),U(e,o)&&m(r[0],r[0],ur),B(e,r[0]),m(e,e,i),U(e,o)?-1:(d(r[0])===t[31]>>7&&M(r[0],er,r[0]),m(r[3],r[0],r[1]),0)}function j(r,t,n,e){var i,h,a=new Uint8Array(32),f=new Uint8Array(64),s=[$(),$(),$(),$()],u=[$(),$(),$(),$()];if(h=-1,n<64)return-1;if(D(u,e))return-1;for(i=0;i<n;i++)r[i]=t[i];for(i=0;i<32;i++)r[i+32]=e[i];if(N(f,r,n),V(f),I(s,u,f),G(u,t.subarray(32)),O(s,u),F(a,s),n-=64,o(t,0,a,0)){for(i=0;i<n;i++)r[i]=0;return-1}for(i=0;i<n;i++)r[i]=t[i+64];return h=n}function H(r,t){if(r.length!==br)throw new Error("bad key size");if(t.length!==gr)throw new Error("bad nonce size")}function J(r,t){if(r.length!==Er)throw new Error("bad public key size");if(t.length!==xr)throw new Error("bad secret key size")}function Q(){for(var r=0;r<arguments.length;r++)if(!(arguments[r]instanceof Uint8Array))throw new TypeError("unexpected type, use Uint8Array")}function W(r){for(var t=0;t<r.length;t++)r[t]=0}var $=function(r){var t,n=new Float64Array(16);if(r)for(t=0;t<r.length;t++)n[t]=r[t];return n},rr=function(){throw new Error("no PRNG")},tr=new Uint8Array(16),nr=new Uint8Array(32);nr[0]=9;var er=$(),or=$([1]),ir=$([56129,1]),hr=$([30883,4953,19914,30187,55467,16705,2637,112,59544,30585,16505,36039,65139,11119,27886,20995]),ar=$([61785,9906,39828,60374,45398,33411,5274,224,53552,61171,33010,6542,64743,22239,55772,9222]),fr=$([54554,36645,11616,51542,42930,38181,51040,26924,56412,64982,57905,49316,21502,52590,14035,8553]),sr=$([26200,26214,26214,26214,26214,26214,26214,26214,26214,26214,26214,26214,26214,26214,26214,26214]),ur=$([41136,18958,6951,50414,58488,44335,6150,12099,55207,15867,153,11085,57099,20417,9344,11139]),cr=new Uint8Array([101,120,112,97,110,100,32,51,50,45,98,121,116,101,32,107]),yr=function(r){this.buffer=new Uint8Array(16),this.r=new Uint16Array(10),this.h=new Uint16Array(10),this.pad=new Uint16Array(8),this.leftover=0,this.fin=0;var t,n,e,o,i,h,a,f;t=255&r[0]|(255&r[1])<<8,this.r[0]=8191&t,n=255&r[2]|(255&r[3])<<8,this.r[1]=8191&(t>>>13|n<<3),e=255&r[4]|(255&r[5])<<8,this.r[2]=7939&(n>>>10|e<<6),o=255&r[6]|(255&r[7])<<8,this.r[3]=8191&(e>>>7|o<<9),i=255&r[8]|(255&r[9])<<8,this.r[4]=255&(o>>>4|i<<12),this.r[5]=i>>>1&8190,h=255&r[10]|(255&r[11])<<8,this.r[6]=8191&(i>>>14|h<<2),a=255&r[12]|(255&r[13])<<8,this.r[7]=8065&(h>>>11|a<<5),f=255&r[14]|(255&r[15])<<8,this.r[8]=8191&(a>>>8|f<<8),this.r[9]=f>>>5&127,this.pad[0]=255&r[16]|(255&r[17])<<8,this.pad[1]=255&r[18]|(255&r[19])<<8,this.pad[2]=255&r[20]|(255&r[21])<<8,this.pad[3]=255&r[22]|(255&r[23])<<8,this.pad[4]=255&r[24]|(255&r[25])<<8,this.pad[5]=255&r[26]|(255&r[27])<<8,this.pad[6]=255&r[28]|(255&r[29])<<8,this.pad[7]=255&r[30]|(255&r[31])<<8};yr.prototype.blocks=function(r,t,n){for(var e,o,i,h,a,f,s,u,c,y,l,w,v,p,b,g,_,A,U,d=this.fin?0:2048,E=this.h[0],x=this.h[1],M=this.h[2],m=this.h[3],B=this.h[4],S=this.h[5],K=this.h[6],Y=this.h[7],k=this.h[8],T=this.h[9],L=this.r[0],z=this.r[1],R=this.r[2],P=this.r[3],N=this.r[4],O=this.r[5],C=this.r[6],F=this.r[7],I=this.r[8],G=this.r[9];n>=16;)e=255&r[t+0]|(255&r[t+1])<<8,E+=8191&e,o=255&r[t+2]|(255&r[t+3])<<8,x+=8191&(e>>>13|o<<3),i=255&r[t+4]|(255&r[t+5])<<8,M+=8191&(o>>>10|i<<6),h=255&r[t+6]|(255&r[t+7])<<8,m+=8191&(i>>>7|h<<9),a=255&r[t+8]|(255&r[t+9])<<8,B+=8191&(h>>>4|a<<12),S+=a>>>1&8191,f=255&r[t+10]|(255&r[t+11])<<8,K+=8191&(a>>>14|f<<2),s=255&r[t+12]|(255&r[t+13])<<8,Y+=8191&(f>>>11|s<<5),u=255&r[t+14]|(255&r[t+15])<<8,k+=8191&(s>>>8|u<<8),T+=u>>>5|d,c=0,y=c,y+=E*L,y+=x*(5*G),y+=M*(5*I),y+=m*(5*F),y+=B*(5*C),c=y>>>13,y&=8191,y+=S*(5*O),y+=K*(5*N),y+=Y*(5*P),y+=k*(5*R),y+=T*(5*z),c+=y>>>13,y&=8191,l=c,l+=E*z,l+=x*L,l+=M*(5*G),l+=m*(5*I),l+=B*(5*F),c=l>>>13,l&=8191,l+=S*(5*C),l+=K*(5*O),l+=Y*(5*N),l+=k*(5*P),l+=T*(5*R),c+=l>>>13,l&=8191,w=c,w+=E*R,w+=x*z,w+=M*L,w+=m*(5*G),w+=B*(5*I),c=w>>>13,w&=8191,w+=S*(5*F),w+=K*(5*C),w+=Y*(5*O),w+=k*(5*N),w+=T*(5*P),c+=w>>>13,w&=8191,v=c,v+=E*P,v+=x*R,v+=M*z,v+=m*L,v+=B*(5*G),c=v>>>13,v&=8191,v+=S*(5*I),v+=K*(5*F),v+=Y*(5*C),v+=k*(5*O),v+=T*(5*N),c+=v>>>13,v&=8191,p=c,p+=E*N,p+=x*P,p+=M*R,p+=m*z,p+=B*L,c=p>>>13,p&=8191,p+=S*(5*G),p+=K*(5*I),p+=Y*(5*F),p+=k*(5*C),p+=T*(5*O),c+=p>>>13,p&=8191,b=c,b+=E*O,b+=x*N,b+=M*P,b+=m*R,b+=B*z,c=b>>>13,b&=8191,b+=S*L,b+=K*(5*G),b+=Y*(5*I),b+=k*(5*F),b+=T*(5*C),c+=b>>>13,b&=8191,g=c,g+=E*C,g+=x*O,g+=M*N,g+=m*P,g+=B*R,c=g>>>13,g&=8191,g+=S*z,g+=K*L,g+=Y*(5*G),g+=k*(5*I),g+=T*(5*F),c+=g>>>13,g&=8191,_=c,_+=E*F,_+=x*C,_+=M*O,_+=m*N,_+=B*P,c=_>>>13,_&=8191,_+=S*R,_+=K*z,_+=Y*L,_+=k*(5*G),_+=T*(5*I),c+=_>>>13,_&=8191,A=c,A+=E*I,A+=x*F,A+=M*C,A+=m*O,A+=B*N,c=A>>>13,A&=8191,A+=S*P,A+=K*R,A+=Y*z,A+=k*L,A+=T*(5*G),c+=A>>>13,A&=8191,U=c,U+=E*G,U+=x*I,U+=M*F,U+=m*C,U+=B*O,c=U>>>13,U&=8191,U+=S*N,U+=K*P,U+=Y*R,U+=k*z,U+=T*L,c+=U>>>13,U&=8191,c=(c<<2)+c|0,c=c+y|0,y=8191&c,c>>>=13,l+=c,E=y,x=l,M=w,m=v,B=p,S=b,K=g,Y=_,k=A,T=U,t+=16,n-=16;this.h[0]=E,this.h[1]=x,this.h[2]=M,this.h[3]=m,this.h[4]=B,this.h[5]=S,this.h[6]=K,this.h[7]=Y,this.h[8]=k,this.h[9]=T},yr.prototype.finish=function(r,t){var n,e,o,i,h=new Uint16Array(10);if(this.leftover){for(i=this.leftover,this.buffer[i++]=1;i<16;i++)this.buffer[i]=0;this.fin=1,this.blocks(this.buffer,0,16)}for(n=this.h[1]>>>13,this.h[1]&=8191,i=2;i<10;i++)this.h[i]+=n,n=this.h[i]>>>13,this.h[i]&=8191;for(this.h[0]+=5*n,n=this.h[0]>>>13,this.h[0]&=8191,this.h[1]+=n,n=this.h[1]>>>13,this.h[1]&=8191,this.h[2]+=n,h[0]=this.h[0]+5,n=h[0]>>>13,h[0]&=8191,i=1;i<10;i++)h[i]=this.h[i]+n,n=h[i]>>>13,h[i]&=8191;for(h[9]-=8192,e=(1^n)-1,i=0;i<10;i++)h[i]&=e;for(e=~e,i=0;i<10;i++)this.h[i]=this.h[i]&e|h[i];for(this.h[0]=65535&(this.h[0]|this.h[1]<<13),this.h[1]=65535&(this.h[1]>>>3|this.h[2]<<10),this.h[2]=65535&(this.h[2]>>>6|this.h[3]<<7),this.h[3]=65535&(this.h[3]>>>9|this.h[4]<<4),this.h[4]=65535&(this.h[4]>>>12|this.h[5]<<1|this.h[6]<<14),this.h[5]=65535&(this.h[6]>>>2|this.h[7]<<11),this.h[6]=65535&(this.h[7]>>>5|this.h[8]<<8),this.h[7]=65535&(this.h[8]>>>8|this.h[9]<<5),o=this.h[0]+this.pad[0],this.h[0]=65535&o,i=1;i<8;i++)o=(this.h[i]+this.pad[i]|0)+(o>>>16)|0,this.h[i]=65535&o;r[t+0]=this.h[0]>>>0&255,r[t+1]=this.h[0]>>>8&255,r[t+2]=this.h[1]>>>0&255,r[t+3]=this.h[1]>>>8&255,r[t+4]=this.h[2]>>>0&255,r[t+5]=this.h[2]>>>8&255,r[t+6]=this.h[3]>>>0&255,r[t+7]=this.h[3]>>>8&255,r[t+8]=this.h[4]>>>0&255,r[t+9]=this.h[4]>>>8&255,r[t+10]=this.h[5]>>>0&255,r[t+11]=this.h[5]>>>8&255,r[t+12]=this.h[6]>>>0&255,r[t+13]=this.h[6]>>>8&255,r[t+14]=this.h[7]>>>0&255,r[t+15]=this.h[7]>>>8&255},yr.prototype.update=function(r,t,n){var e,o;if(this.leftover){for(o=16-this.leftover,o>n&&(o=n),e=0;e<o;e++)this.buffer[this.leftover+e]=r[t+e];if(n-=o,t+=o,this.leftover+=o,this.leftover<16)return;this.blocks(this.buffer,0,16),this.leftover=0}if(n>=16&&(o=n-n%16,this.blocks(r,t,o),t+=o,n-=o),n){for(e=0;e<n;e++)this.buffer[this.leftover+e]=r[t+e];this.leftover+=n}};var lr=v,wr=p,vr=[1116352408,3609767458,1899447441,602891725,3049323471,3964484399,3921009573,2173295548,961987163,4081628472,1508970993,3053834265,2453635748,2937671579,2870763221,3664609560,3624381080,2734883394,310598401,1164996542,607225278,1323610764,1426881987,3590304994,1925078388,4068182383,2162078206,991336113,2614888103,633803317,3248222580,3479774868,3835390401,2666613458,4022224774,944711139,264347078,2341262773,604807628,2007800933,770255983,1495990901,1249150122,1856431235,1555081692,3175218132,1996064986,2198950837,2554220882,3999719339,2821834349,766784016,2952996808,2566594879,3210313671,3203337956,3336571891,1034457026,3584528711,2466948901,113926993,3758326383,338241895,168717936,666307205,1188179964,773529912,1546045734,1294757372,1522805485,1396182291,2643833823,1695183700,2343527390,1986661051,1014477480,2177026350,1206759142,2456956037,344077627,2730485921,1290863460,2820302411,3158454273,3259730800,3505952657,3345764771,106217008,3516065817,3606008344,3600352804,1432725776,4094571909,1467031594,275423344,851169720,430227734,3100823752,506948616,1363258195,659060556,3750685593,883997877,3785050280,958139571,3318307427,1322822218,3812723403,1537002063,2003034995,1747873779,3602036899,1955562222,1575990012,2024104815,1125592928,2227730452,2716904306,2361852424,442776044,2428436474,593698344,2756734187,3733110249,3204031479,2999351573,3329325298,3815920427,3391569614,3928383900,3515267271,566280711,3940187606,3454069534,4118630271,4000239992,116418474,1914138554,174292421,2731055270,289380356,3203993006,460393269,320620315,685471733,587496836,852142971,1086792851,1017036298,365543100,1126000580,2618297676,1288033470,3409855158,1501505948,4234509866,1607167915,987167468,1816402316,1246189591],pr=new Float64Array([237,211,245,92,26,99,18,88,214,156,247,162,222,249,222,20,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,16]),br=32,gr=24,_r=32,Ar=16,Ur=32,dr=32,Er=32,xr=32,Mr=32,mr=gr,Br=_r,Sr=Ar,Kr=64,Yr=32,kr=64,Tr=32,Lr=64;r.lowlevel={crypto_core_hsalsa20:f,crypto_stream_xor:y,crypto_stream:c,crypto_stream_salsa20_xor:s,crypto_stream_salsa20:u,crypto_onetimeauth:l,crypto_onetimeauth_verify:w,crypto_verify_16:e,crypto_verify_32:o,crypto_secretbox:v,crypto_secretbox_open:p,crypto_scalarmult:Y,crypto_scalarmult_base:k,crypto_box_beforenm:L,crypto_box_afternm:lr,crypto_box:z,crypto_box_open:R,crypto_box_keypair:T,crypto_hash:N,crypto_sign:X,crypto_sign_keypair:Z,crypto_sign_open:j,crypto_secretbox_KEYBYTES:br,crypto_secretbox_NONCEBYTES:gr,crypto_secretbox_ZEROBYTES:_r,crypto_secretbox_BOXZEROBYTES:Ar,crypto_scalarmult_BYTES:Ur,crypto_scalarmult_SCALARBYTES:dr,crypto_box_PUBLICKEYBYTES:Er,crypto_box_SECRETKEYBYTES:xr,crypto_box_BEFORENMBYTES:Mr,crypto_box_NONCEBYTES:mr,crypto_box_ZEROBYTES:Br,crypto_box_BOXZEROBYTES:Sr,crypto_sign_BYTES:Kr,crypto_sign_PUBLICKEYBYTES:Yr,crypto_sign_SECRETKEYBYTES:kr,crypto_sign_SEEDBYTES:Tr,crypto_hash_BYTES:Lr},r.randomBytes=function(r){var t=new Uint8Array(r);return rr(t,r),t},r.secretbox=function(r,t,n){Q(r,t,n),H(n,t);for(var e=new Uint8Array(_r+r.length),o=new Uint8Array(e.length),i=0;i<r.length;i++)e[i+_r]=r[i];return v(o,e,e.length,t,n),o.subarray(Ar)},r.secretbox.open=function(r,t,n){Q(r,t,n),H(n,t);for(var e=new Uint8Array(Ar+r.length),o=new Uint8Array(e.length),i=0;i<r.length;i++)e[i+Ar]=r[i];return e.length<32?null:0!==p(o,e,e.length,t,n)?null:o.subarray(_r)},r.secretbox.keyLength=br,r.secretbox.nonceLength=gr,r.secretbox.overheadLength=Ar,r.scalarMult=function(r,t){if(Q(r,t),r.length!==dr)throw new Error("bad n size");if(t.length!==Ur)throw new Error("bad p size");var n=new Uint8Array(Ur);return Y(n,r,t),n},r.scalarMult.base=function(r){if(Q(r),r.length!==dr)throw new Error("bad n size");var t=new Uint8Array(Ur);return k(t,r),t},r.scalarMult.scalarLength=dr,r.scalarMult.groupElementLength=Ur,r.box=function(t,n,e,o){var i=r.box.before(e,o);return r.secretbox(t,n,i)},r.box.before=function(r,t){Q(r,t),J(r,t);var n=new Uint8Array(Mr);return L(n,r,t),n},r.box.after=r.secretbox,r.box.open=function(t,n,e,o){var i=r.box.before(e,o);return r.secretbox.open(t,n,i)},r.box.open.after=r.secretbox.open,r.box.keyPair=function(){var r=new Uint8Array(Er),t=new Uint8Array(xr);return T(r,t),{publicKey:r,secretKey:t}},r.box.keyPair.fromSecretKey=function(r){if(Q(r),r.length!==xr)throw new Error("bad secret key size");var t=new Uint8Array(Er);return k(t,r),{publicKey:t,secretKey:new Uint8Array(r)}},r.box.publicKeyLength=Er,r.box.secretKeyLength=xr,r.box.sharedKeyLength=Mr,r.box.nonceLength=mr,r.box.overheadLength=r.secretbox.overheadLength,r.sign=function(r,t){if(Q(r,t),t.length!==kr)throw new Error("bad secret key size");var n=new Uint8Array(Kr+r.length);return X(n,r,r.length,t),n},r.sign.open=function(r,t){if(Q(r,t),t.length!==Yr)throw new Error("bad public key size");var n=new Uint8Array(r.length),e=j(n,r,r.length,t);if(e<0)return null;for(var o=new Uint8Array(e),i=0;i<o.length;i++)o[i]=n[i];return o},r.sign.detached=function(t,n){for(var e=r.sign(t,n),o=new Uint8Array(Kr),i=0;i<o.length;i++)o[i]=e[i];return o},r.sign.detached.verify=function(r,t,n){if(Q(r,t,n),t.length!==Kr)throw new Error("bad signature size");if(n.length!==Yr)throw new Error("bad public key size");var e,o=new Uint8Array(Kr+r.length),i=new Uint8Array(Kr+r.length);for(e=0;e<Kr;e++)o[e]=t[e];for(e=0;e<r.length;e++)o[e+Kr]=r[e];return j(i,o,o.length,n)>=0},r.sign.keyPair=function(){var r=new Uint8Array(Yr),t=new Uint8Array(kr);return Z(r,t),{publicKey:r,secretKey:t}},r.sign.keyPair.fromSecretKey=function(r){if(Q(r),r.length!==kr)throw new Error("bad secret key size");for(var t=new Uint8Array(Yr),n=0;n<t.length;n++)t[n]=r[32+n];return{publicKey:t,secretKey:new Uint8Array(r)}},r.sign.keyPair.fromSeed=function(r){if(Q(r),r.length!==Tr)throw new Error("bad seed size");for(var t=new Uint8Array(Yr),n=new Uint8Array(kr),e=0;e<32;e++)n[e]=r[e];return Z(t,n,!0),{publicKey:t,secretKey:n}},r.sign.publicKeyLength=Yr,r.sign.secretKeyLength=kr,r.sign.seedLength=Tr,r.sign.signatureLength=Kr,r.hash=function(r){Q(r);var t=new Uint8Array(Lr);return N(t,r,r.length),t},r.hash.hashLength=Lr,r.verify=function(r,t){return Q(r,t),0!==r.length&&0!==t.length&&(r.length===t.length&&0===n(r,0,t,0,r.length))},r.setPRNG=function(r){rr=r},function(){var t="undefined"!=typeof self?self.crypto||self.msCrypto:null;if(t&&t.getRandomValues){var n=65536;r.setPRNG(function(r,e){var o,i=new Uint8Array(e);for(o=0;o<e;o+=n)t.getRandomValues(i.subarray(o,o+Math.min(e-o,n)));for(o=0;o<e;o++)r[o]=i[o];W(i)})}else"undefined"!=typeof require&&(t=require("crypto"),
t&&t.randomBytes&&r.setPRNG(function(r,n){var e,o=t.randomBytes(n);for(e=0;e<n;e++)r[e]=o[e];W(o)}))}()}("undefined"!=typeof module&&module.exports?module.exports:self.nacl=self.nacl||{});