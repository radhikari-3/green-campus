const qrImage = document.getElementById('qrImage');
        const downloadBtn = document.getElementById('downloadBtn');

        downloadBtn.addEventListener('click', function (e) {
          e.preventDefault();
          const base64Data = qrImage.src.split(',')[1];
          const byteCharacters = atob(base64Data);
          const byteNumbers = new Array(byteCharacters.length);
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
          }
          const byteArray = new Uint8Array(byteNumbers);
          const blob = new Blob([byteArray], { type: 'image/png' });
          const url = URL.createObjectURL(blob);

          const link = document.createElement('a');
          link.href = url;
          link.download = 'eco_voucher.png';
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        });