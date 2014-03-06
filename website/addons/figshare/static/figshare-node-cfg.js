    $(document).ready(function() {


        $('#figshareAddKey').on('click', function() {
            var self = $(this)[0];
            $.ajax({
                type: 'POST',
                url: nodeApiUrl + 'figshare/user_auth/',
                contentType: 'application/json',
                dataType: 'json',
                success: function(response) {
                  if(self.outerText == 'Authorize: Create Access Token')
                      window.location.href = nodeApiUrl + 'figshare/oauth/';
                  else
                      window.location.reload();
                }
            });

        });

        $('#figshareDelKey').on('click', function() {
            bootbox.confirm(
                'Are you sure you want to delete your Figshare access key? This will ' +
                'revoke the ability to modify and upload files to Figshare. If ' +
                'the associated repo is private, this will also disable viewing ' +
                'and downloading files from Figshare.',
                function(result) {
                    if (result) {
                        $.ajax({
                            url: nodeApiUrl + 'figshare/oauth/',
                            type: 'DELETE',
                            contentType: 'application/json',
                            dataType: 'json',
                            success: function() {
                                window.location.reload();
                            }
                        });
                    }
                }
            );
        });

        $('#figshareSelectProject').on('change', function() {
            var value = $(this).val();
            if (value) {
                $('#figshareId').val(value)
                $('#figshareTitle').val($('#figshareSelectProject option:selected').text())
            }
        });

    });
